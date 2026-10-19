"""점수 매기는 방법들. overlap·bigram은 표준 라이브러리, embed는 외부 패키지(sentence-transformers)가 필요하다."""
from __future__ import annotations

import re


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s,.()·/'\"“”‘’—–\-:;?!]+", text) if len(w) >= 2]


def overlap(query: str, candidates: dict[str, str]) -> dict[str, float]:
    """지금 엔진(proviso.query.search)과 같은 낱말 겹침: 질문 낱말이 후보 글에 들어 있으면 1점(끝 글자 하나 뗀 것도)."""
    words = _words(query)
    out = {}
    for cid, text in candidates.items():
        out[cid] = sum(1 for w in words if w in text or (len(w) > 2 and w[:-1] in text))
    return out


def _bigrams(text: str) -> set[str]:
    t = re.sub(r"\s+", "", text)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def bigram(query: str, candidates: dict[str, str]) -> dict[str, float]:
    """글자 두 개씩 겹침(자카드). 한국어 조사·활용에 덜 흔들린다."""
    q = _bigrams(query)
    out = {}
    for cid, text in candidates.items():
        c = _bigrams(text)
        out[cid] = len(q & c) / len(q | c) if q | c else 0.0
    return out


def make_embed(model_name: str, query_prefix: str = "", passage_prefix: str = ""):
    """문장 임베딩 코사인 유사도. e5 계열은 prefix로 'query: ' / 'passage: '를 붙인다."""
    from sentence_transformers import SentenceTransformer  # 외부 패키지: 이 함수를 쓸 때만 필요

    model = SentenceTransformer(model_name)
    cache: dict[str, object] = {}

    def embed(query: str, candidates: dict[str, str]) -> dict[str, float]:
        key = tuple(sorted(candidates))
        if key not in cache:
            ids = list(candidates)
            vecs = model.encode([passage_prefix + candidates[i] for i in ids], normalize_embeddings=True)
            cache[key] = (ids, vecs)
        ids, vecs = cache[key]
        q = model.encode([query_prefix + query], normalize_embeddings=True)[0]
        return {i: float(v @ q) for i, v in zip(ids, vecs)}

    return embed


def make_onnx_embed(repo: str, onnx_file: str = "onnx/model.onnx", pooling: str = "mean",
                    query_prefix: str = "", passage_prefix: str = "", max_len: int = 512):
    """PyTorch 없이 ONNX 실행기로 문장 임베딩(코사인 유사도). 외부 패키지: onnxruntime, tokenizers, huggingface_hub, numpy.

    pooling: "mean"(e5·MiniLM 계열, 패딩 뺀 평균) / "cls"(bge 계열, 첫 토큰).
    """
    import numpy as np
    import onnxruntime as ort
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(hf_hub_download(repo, "tokenizer.json"))
    tok.enable_truncation(max_len)
    tok.enable_padding()
    sess = ort.InferenceSession(hf_hub_download(repo, onnx_file), providers=["CPUExecutionProvider"])
    names = {i.name for i in sess.get_inputs()}

    def encode(texts: list[str]):
        enc = tok.encode_batch(texts)
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in names:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = sess.run(None, feed)[0]  # (문장, 토큰, 차원)
        if pooling == "cls":
            vec = hidden[:, 0]
        else:
            m = mask[..., None].astype(hidden.dtype)
            vec = (hidden * m).sum(1) / m.sum(1)
        return vec / np.linalg.norm(vec, axis=1, keepdims=True)

    cache: dict[tuple, tuple] = {}

    def embed(query: str, candidates: dict[str, str]) -> dict[str, float]:
        key = tuple(sorted(candidates))
        if key not in cache:
            ids = list(candidates)
            cache[key] = (ids, encode([passage_prefix + candidates[i] for i in ids]))
        ids, vecs = cache[key]
        q = encode([query_prefix + query])[0]
        return {i: float(v @ q) for i, v in zip(ids, vecs)}

    return embed

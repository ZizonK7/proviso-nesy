"""Colab에 올릴 노트북과 CSV 묶음 만들기: python -m eda.colab.

표준 라이브러리만 사용. 분석 셀은 start.ipynb에서 가져오며 결과는 out/eda_colab/에 둔다.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import textwrap
import zipfile
from pathlib import Path

from eda.export import ROOT, export

OUT = ROOT / "out" / "eda_colab"


def cell(kind: str, source: str) -> dict:
    result = {"cell_type": kind, "metadata": {}, "source": textwrap.dedent(source).strip().splitlines(True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


SETUP = '''
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_colwidth", 80)
plt.rcParams["axes.unicode_minus"] = False

BUNDLE = Path("proviso_eda_data.zip")
if not BUNDLE.is_file():
    from google.colab import files
    print("proviso_eda_data.zip 파일을 선택해 주세요.")
    uploaded = files.upload()
    if len(uploaded) != 1 or not next(iter(uploaded)).endswith(".zip"):
        raise ValueError("데이터 ZIP 하나만 선택해 주세요.")
    BUNDLE.write_bytes(next(iter(uploaded.values())))

# ZIP 안에서 바로 읽습니다. 저장소 코드나 GitHub 로그인은 필요하지 않습니다.
with zipfile.ZipFile(BUNDLE) as z:
    manifest = json.loads(z.read("manifest.json"))
    T = {}
    for name, info in manifest["tables"].items():
        data = z.read(name + ".csv")
        if hashlib.sha256(data).hexdigest() != info["sha256"]:
            raise ValueError(f"{name}: 데이터 해시가 다릅니다. ZIP을 다시 준비해 주세요.")
        try:
            table = pd.read_csv(io.BytesIO(data), low_memory=False)
        except pd.errors.EmptyDataError:
            if info["rows"] != 0:
                raise
            table = pd.DataFrame()
        if len(table) != info["rows"]:
            raise ValueError(f"{name}: 행 수가 다릅니다.")
        T[name] = table

nodes, edges, judgments = T["nodes"], T["edges"], T["judgments"]
disp, rules, fb = T["dispatches"], T["dispatch_rules"], T["feedback"]
print("데이터 생성 시각 (UTC):", manifest["created_at"])
print("원본 커밋:", manifest["commit"])
print("생성 시 미커밋 변경:", manifest["dirty"])
display(pd.DataFrame({name: {"행": len(t), "열": len(t.columns)} for name, t in T.items()}).T)
'''

FONT = '''
# 그래프를 그리기 전 한 번 실행하세요. 표만 볼 때는 건너뛰어도 됩니다.
import subprocess
from matplotlib import font_manager

font_path = Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf")
if not font_path.is_file():
    subprocess.run(["apt-get", "-qq", "update"], check=True)
    subprocess.run(["apt-get", "-qq", "install", "-y", "fonts-nanum"], check=True)
font_manager.fontManager.addfont(str(font_path))
plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(font_path)).get_name()
print("한글 글꼴 준비 완료")
'''


def prepare(out: Path = OUT) -> tuple[Path, Path]:
    out.mkdir(parents=True, exist_ok=True)
    counts = export(ROOT / "out" / "eda")
    manifest = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "tables": {},
    }
    bundle = out / "proviso_eda_data.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, rows in counts.items():
            data = (ROOT / "out" / "eda" / f"{name}.csv").read_bytes()
            manifest["tables"][name] = {"rows": rows, "sha256": hashlib.sha256(data).hexdigest()}
            z.writestr(f"{name}.csv", data)
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    notebook = json.loads((ROOT / "eda" / "start.ipynb").read_text(encoding="utf-8"))
    intro = '''
    # 논리집 EDA — Colab 시작

    1. 이 노트북을 Colab에서 열고 **CPU 런타임**에 연결하세요. GPU는 필요 없습니다.
    2. 첫 코드 셀을 실행하고 `proviso_eda_data.zip`을 선택하세요. ZIP은 풀지 않습니다.
    3. 표의 행·열 수가 보이면 준비 완료입니다. 우선 여기서 멈추고 결과를 함께 봅니다.
    4. 그래프 전에는 한글 글꼴 셀을 실행하세요. 이후 분석 셀은 기존 `eda/start.ipynb`와 같습니다.

    데이터는 ZIP을 만든 시점의 스냅샷입니다. 원본이 바뀌면 로컬에서 `python -m eda.colab`으로
    다시 만들고 Colab의 기존 ZIP을 지운 뒤 새 ZIP을 올리세요.
    far_fields는 AI가 생성한 큰 묶음이므로 다른 분야와 분리해서 봅니다.
    '''
    notebook["cells"] = [cell("markdown", intro), cell("code", SETUP),
                         cell("markdown", "## 한글 글꼴 (그래프를 보기 전)"), cell("code", FONT),
                         *notebook["cells"][4:]]
    for i, c in enumerate(notebook["cells"]):
        c["id"] = f"colab-{i:02}"
        if c["cell_type"] == "code":
            c.update(execution_count=None, outputs=[])
    notebook["metadata"]["colab"] = {"name": "proviso_eda_colab.ipynb", "provenance": []}
    path = out / "proviso_eda_colab.ipynb"
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path, bundle


if __name__ == "__main__":
    for path in prepare():
        print(path)

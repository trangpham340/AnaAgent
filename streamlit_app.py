import json
import os
import urllib.error
import urllib.request

import pandas as pd
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://endpoint-afe1f857-2970-4f3b-acf6-a26e8730331c.agentbase-runtime.aiplatform.vngcloud.vn",
).rstrip("/")


def split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def post_analysis(payload: dict) -> tuple[dict | None, str | None]:
    request = urllib.request.Request(
        f"{API_BASE_URL}/api/v1/analyze",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        return None, f"API returned {exc.code}: {detail}"
    except urllib.error.URLError as exc:
        return None, f"Could not reach API at {API_BASE_URL}: {exc.reason}"
    except TimeoutError:
        return None, "The API request timed out."


def render_response(result: dict) -> None:
    st.subheader("Business summary")
    st.write(result["summary"])

    st.subheader("Findings")
    for finding in result["findings"]:
        severity = finding.get("severity", "medium").upper()
        with st.container(border=True):
            st.markdown(f"**{finding['title']}**")
            st.caption(f"Severity: {severity}")
            st.write(finding["detail"])
            st.markdown("**Recommendation**")
            st.write(finding["recommendation"])

    st.subheader("Next steps")
    for index, step in enumerate(result["next_steps"], start=1):
        st.write(f"{index}. {step}")

    st.caption(f"Source: {result['source']} | Model: {result['model_used']}")


def read_uploaded_file() -> str:
    uploaded_file = st.file_uploader("Upload Excel, CSV, or TXT", type=["xlsx", "xls", "csv", "txt"])
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()
    if file_name.endswith((".xlsx", ".xls")):
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        content_blocks = []
        for sheet_name, sheet in sheets.items():
            content_blocks.append(f"Sheet: {sheet_name}\n{sheet.to_csv(index=False)}")
        return "\n\n".join(content_blocks)

    return uploaded_file.getvalue().decode("utf-8", errors="replace")


def main() -> None:
    st.set_page_config(page_title="Analysis Agent AI", page_icon="AI", layout="wide")

    st.title("Analysis Agent AI")
    st.caption(f"FastAPI backend: {API_BASE_URL}")

    with st.sidebar:
        st.header("Input")
        project_name = st.text_input("Project or report name", value="Weekly performance review")
        goals = st.text_area(
            "Goals",
            value="Identify business performance drivers\nFind risks and next-week actions",
            height=120,
        )
        constraints = st.text_area(
            "Constraints",
            value="Do not overclaim causality without campaign context",
            height=100,
        )

    uploaded_content = read_uploaded_file()
    manual_content = st.text_area(
        "Business data, requirements, notes, or source summary",
        value=uploaded_content,
        height=320,
        placeholder="Paste weekly performance data, CSV rows, requirements, or project notes here.",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit = st.button("Analyze", type="primary", use_container_width=True)
    with col2:
        st.caption("The UI sends this request to the FastAPI `/api/v1/analyze` endpoint.")

    if not submit:
        return

    payload = {
        "project_name": project_name,
        "content": manual_content,
        "goals": split_lines(goals),
        "constraints": split_lines(constraints),
    }

    if not payload["project_name"].strip():
        st.error("Project or report name is required.")
        return

    if len(payload["content"].strip()) < 10:
        st.error("Content must contain at least 10 characters.")
        return

    with st.spinner("Analyzing with FastAPI backend..."):
        result, error = post_analysis(payload)

    if error:
        st.error(error)
        return

    render_response(result)


if __name__ == "__main__":
    main()

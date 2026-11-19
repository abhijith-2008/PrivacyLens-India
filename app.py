
import io
import html
import hashlib

import streamlit as st
from pypdf import PdfReader

from report import build_report
from dpdp_checklist import build_dpdp_checklist


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="PrivacyLens India",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 PrivacyLens India")

st.caption(
    "Understand privacy policies through plain-language summaries, "
    "ML-assisted findings, and an informational DPDP checklist."
)

st.info(
    "This tool provides informational findings, not legal advice "
    "or a determination of DPDP compliance."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

st.header("Upload or paste a privacy policy")

uploaded_file = st.file_uploader(
    "Upload a privacy policy",
    type=["txt", "pdf"],
    help="Supported formats: PDF and TXT",
)

uploaded_text = ""

if uploaded_file is not None:

    try:
        file_bytes = uploaded_file.getvalue()

        # TXT FILE EXTRACTION
        if uploaded_file.name.lower().endswith(".txt"):

            try:
                uploaded_text = file_bytes.decode("utf-8-sig")

            except UnicodeDecodeError:
                uploaded_text = file_bytes.decode("cp1252")

        # PDF FILE EXTRACTION
        elif uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PdfReader(io.BytesIO(file_bytes))

            uploaded_text = "\n\n".join(
                page.extract_text() or ""
                for page in pdf_reader.pages
            )

            if not uploaded_text.strip():
                st.error(
                    "No selectable text was found in this PDF. "
                    "It may be a scanned document. Please use a "
                    "text-based PDF or paste its text manually."
                )

        # UPDATE SESSION STATE WHEN A NEW FILE IS UPLOADED
        if uploaded_text.strip():

            st.success(
                f"Successfully extracted text from {uploaded_file.name}"
            )

            file_hash = hashlib.sha256(file_bytes).hexdigest()

            if st.session_state.get("loaded_file_hash") != file_hash:

                st.session_state["policy_input"] = uploaded_text

                st.session_state["loaded_file_hash"] = file_hash

    except Exception as exc:

        st.error(f"Could not read the uploaded file: {exc}")


# --------------------------------------------------
# POLICY TEXT INPUT
# --------------------------------------------------

policy_text = st.text_area(
    "Privacy policy text",
    height=280,
    placeholder=(
        "Upload a PDF/TXT file above or paste the privacy policy here..."
    ),
    key="policy_input",
)


# --------------------------------------------------
# ANALYZE BUTTON
# --------------------------------------------------

analyze = st.button(
    "🔍 Analyze Policy",
    type="primary",
    disabled=not policy_text.strip(),
    use_container_width=True,
)


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if analyze:

    with st.spinner("Analyzing your privacy policy..."):

        try:

            report = build_report(policy_text)

            checklist_result = build_dpdp_checklist(
                policy_text,
                include_model_report=False,
            )

            st.success("Analysis completed successfully!")


            # ------------------------------------------
            # 1. EXTRACTIVE SUMMARY
            # ------------------------------------------

            st.header("1. Plain-language overview")

            st.caption(
                "These sentences are selected from your original text; "
                "they are not newly generated claims."
            )

            if report["summary_sentences"]:

                for sentence in report["summary_sentences"]:
                    st.markdown(f"- {sentence}")

            else:

                st.write("No summary sentences could be extracted.")


            # ------------------------------------------
            # 2. ML FINDINGS
            # ------------------------------------------

            st.header("2. Privacy-practice findings")

            st.caption(
                "ML-assisted predictions based on OPP-115 privacy-practice "
                "categories. These are not DPDP compliance classifications. "
                "Only predictions meeting the configured model threshold "
                "are shown as findings."
            )

            if report["findings"]:

                for finding in report["findings"]:

                    evidence_count = len(finding["evidence"])

                    with st.container(border=True):

                        with st.expander(
                            f'🔵 {finding["category"]} '
                            f'({evidence_count} evidence excerpt(s))'
                        ):

                            st.markdown(
                                '<span style="color:#6366F1; '
                                'font-weight:600;">'
                                'ML-predicted privacy practice'
                                '</span>',
                                unsafe_allow_html=True,
                            )

                            st.write(finding["plain_english"])

                            st.markdown("**Evidence from the policy**")

                            if finding["evidence"]:

                                for evidence in finding["evidence"]:

                                    st.markdown(
                                        f'> {evidence["excerpt"]}'
                                    )

                            else:

                                st.info(
                                    "No evidence excerpt was returned. "
                                    "Review the relevant section manually."
                                )

                            st.markdown("**Questions to consider**")

                            for question in finding["review_questions"]:

                                st.markdown(f"- {question}")

            else:

                st.info(
                    "No categories were predicted at the configured "
                    "threshold. This does not mean the policy contains "
                    "no privacy practices."
                )


            # ------------------------------------------
            # 3. DPDP CHECKLIST
            # ------------------------------------------

            st.header("3. Informational DPDP checklist")

            st.caption(
                "Keyword-assisted checks only. A matching phrase is "
                "not proof of compliance, and a missing phrase is not "
                "proof of non-compliance."
            )


            # ------------------------------------------
            # DPDP CARD STYLING
            # ------------------------------------------

            st.markdown(
                """
                <style>

                .dpdp-card {
                    border: 1.5px solid;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                }

                .dpdp-found {
                    border-color: #16A34A;
                    background-color: rgba(22, 163, 74, 0.06);
                }

                .dpdp-missing {
                    border-color: #DC2626;
                    background-color: rgba(220, 38, 38, 0.06);
                }

                .dpdp-title {
                    font-size: 17px;
                    font-weight: 650;
                    margin-bottom: 5px;
                }

                .dpdp-status {
                    font-size: 13px;
                    font-weight: 600;
                }

                </style>
                """,
                unsafe_allow_html=True,
            )


            # ------------------------------------------
            # DPDP CATEGORY RESULTS
            # ------------------------------------------

            for index, item in enumerate(
                checklist_result["checklist"]
            ):

                has_evidence = bool(item["evidence"])

                if has_evidence:

                    card_class = "dpdp-found"
                    status_label = "✓ Potential evidence found"

                else:

                    card_class = "dpdp-missing"
                    status_label = "✕ No matching text found"

                safe_title = html.escape(str(item["title"]))
                safe_status = html.escape(status_label)

               
                st.markdown(
                    f'<div class="dpdp-card {card_class}">'
                    f'<div class="dpdp-title">{safe_title}</div>'
                    f'<div class="dpdp-status">{safe_status}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )



                # --------------------------------------
                # CATEGORY DETAILS
                # --------------------------------------

                with st.expander(
                    f'View details — {item["title"]}'
                ):

                    st.write(item["why_it_matters"])

                    st.caption(
                        f'Reference: {item["reference"]}'
                    )

                    if has_evidence:

                        st.markdown("**Matching excerpts**")

                        for excerpt in item["evidence"]:

                            st.markdown(f"> {excerpt}")

                    else:

                        st.write(
                            "No matching text was found by the "
                            "keyword search."
                        )


            # ------------------------------------------
            # LIMITATIONS
            # ------------------------------------------

            with st.expander("Limitations and interpretation"):

                for limitation in report["limitations"]:

                    st.markdown(f"- {limitation}")

                st.warning(checklist_result["disclaimer"])


        except Exception as exc:

            st.error(
                "The analysis could not be completed. "
                "Check the terminal output for details."
            )

            st.exception(exc)

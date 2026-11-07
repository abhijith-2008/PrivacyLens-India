
import streamlit as st
from report import build_report
from dpdp_checklist import build_dpdp_checklist

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

policy_text = st.text_area(
    "Paste the privacy policy",
    height=280,
    placeholder="Paste the full or relevant part of a privacy policy here...",
)

analyze = st.button(
    "Analyze Policy",
    type="primary",
    disabled=not policy_text.strip(),
)

if analyze:
    with st.spinner("Analyzing your policy..."):
        try:
            report = build_report(policy_text)
            checklist_result = build_dpdp_checklist(
                policy_text,
                include_model_report=False,
            )

            st.success("Analysis complete!")

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

            st.header("2. Privacy-practice findings")

            if report["findings"]:
                for finding in report["findings"]:
                    with st.expander(
                        f'{finding["category"]} '
                        f'({len(finding["evidence"])} evidence excerpt(s))'
                    ):
                        st.write(finding["plain_english"])
                        st.markdown("**Evidence from the policy**")

                        if finding["evidence"]:
                            for evidence in finding["evidence"]:
                                st.markdown(
                                    f'> {evidence["excerpt"]}'
                                )
                        else:
                            st.write(
                                "No evidence excerpt was returned. "
                                "Review the relevant section manually."
                            )

                        st.markdown("**Questions to consider**")
                        for question in finding["review_questions"]:
                            st.markdown(f"- {question}")

            else:
                st.write(
                    "No categories were predicted at the configured "
                    "threshold. This does not mean the policy contains "
                    "no privacy practices."
                )

            st.header("3. Informational DPDP checklist")
            st.caption(
                "Keyword-assisted checks only. A matching phrase is "
                "not proof of compliance, and a missing phrase is not "
                "proof of non-compliance."
            )

            for item in checklist_result["checklist"]:
                with st.expander(
                    f'{item["status"]}: {item["title"]}'
                ):
                    st.write(item["why_it_matters"])
                    st.caption(f'Reference: {item["reference"]}')

                    if item["evidence"]:
                        st.markdown("**Matching excerpts**")
                        for excerpt in item["evidence"]:
                            st.markdown(f"> {excerpt}")
                    else:
                        st.write(
                            "No matching text was found by the "
                            "keyword search."
                        )

            with st.expander("Limitations and interpretation"):
                for limitation in report["limitations"]:
                    st.markdown(f"- {limitation}")

                st.warning(checklist_result["disclaimer"])
                st.write(checklist_result["commencement_note"])

        except Exception as exc:
            st.error(
                "The analysis could not be completed. "
                "Check the terminal output for details."
            )
            st.exception(exc)

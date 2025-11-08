#!/usr/bin/env python3
"""
ClearCraft Lite - Streamlit Cloud Free Tier Version

This is a lightweight version optimized for Streamlit Cloud's free tier.
For full ML features, deploy to HuggingFace Spaces.
"""

import streamlit as st
import textstat
from typing import Optional

# Configure page
st.set_page_config(
    page_title="ClearCraft Lite - Text Clarity Analysis",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def analyze_text(text: str) -> dict:
    """Analyze text readability."""
    return {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
        "sentence_count": textstat.sentence_count(text),
        "lexicon_count": textstat.lexicon_count(text),
        "syllable_count": textstat.syllable_count(text),
    }


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">✨ ClearCraft Lite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Text Readability Analysis</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("About ClearCraft Lite")
        st.write("""
        This is the **Lite version** optimized for Streamlit Cloud's free tier.

        **Features:**
        - 📊 Comprehensive readability metrics
        - 📈 Industry-standard formulas
        - ⚡ Fast analysis

        **For Full Version with:**
        - 🤖 AI-powered rewriting
        - 🔬 Semantic similarity
        - 🎯 Advanced NLP
        - 💬 DeepInfra LLM support

        👉 Deploy to [HuggingFace Spaces](https://huggingface.co/spaces) (free!)
        """)

        st.divider()
        st.caption("**Lite Version** - Streamlit Cloud Free Tier")

    # Main content
    tab1, tab2 = st.tabs(["📊 Analyze Text", "ℹ️ About"])

    with tab1:
        st.header("Text Readability Analysis")

        # Text input
        input_text = st.text_area(
            "Enter your text:",
            height=200,
            placeholder="Paste your text here for readability analysis...",
            help="Enter at least 100 characters for accurate analysis"
        )

        if st.button("🔍 Analyze", use_container_width=True, type="primary"):
            if input_text and len(input_text) >= 10:
                with st.spinner("Analyzing text..."):
                    try:
                        metrics = analyze_text(input_text)

                        st.success("✅ Analysis complete!")

                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Flesch Reading Ease", f"{metrics['flesch_reading_ease']:.1f}")
                            if metrics['flesch_reading_ease'] >= 80:
                                st.caption("🟢 Very Easy")
                            elif metrics['flesch_reading_ease'] >= 60:
                                st.caption("🟡 Easy")
                            elif metrics['flesch_reading_ease'] >= 50:
                                st.caption("🟠 Moderate")
                            else:
                                st.caption("🔴 Difficult")

                        with col2:
                            st.metric("Flesch-Kincaid Grade", f"{metrics['flesch_kincaid_grade']:.1f}")
                            st.caption(f"U.S. Grade {metrics['flesch_kincaid_grade']:.0f}")

                        with col3:
                            st.metric("Gunning Fog Index", f"{metrics['gunning_fog']:.1f}")
                            st.caption("Years of education needed")

                        with col4:
                            st.metric("SMOG Index", f"{metrics['smog_index']:.1f}")
                            st.caption("Reading grade level")

                        st.divider()

                        # Additional metrics
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Word Count", f"{metrics['lexicon_count']:,}")
                            st.caption(f"{metrics['sentence_count']} sentences")

                        with col2:
                            st.metric("Automated Readability", f"{metrics['automated_readability_index']:.1f}")
                            st.caption("ARI score")

                        with col3:
                            st.metric("Dale-Chall Score", f"{metrics['dale_chall_readability_score']:.1f}")
                            st.caption("Difficulty score")

                        # Recommendations
                        st.divider()
                        st.subheader("💡 Recommendations")

                        recommendations = []

                        if metrics['flesch_reading_ease'] < 60:
                            recommendations.append("📖 **Improve readability** - Text is moderately difficult to read")

                        if metrics['flesch_kincaid_grade'] > 12:
                            recommendations.append("🎓 **Simplify vocabulary** - Requires college-level education")

                        if metrics['gunning_fog'] > 12:
                            recommendations.append("✂️ **Shorten sentences** - Average sentence complexity is high")

                        avg_words_per_sentence = metrics['lexicon_count'] / max(metrics['sentence_count'], 1)
                        if avg_words_per_sentence > 25:
                            recommendations.append("📝 **Break up long sentences** - Average length exceeds 25 words")

                        if recommendations:
                            for rec in recommendations:
                                st.write(f"- {rec}")
                        else:
                            st.success("✅ **Text quality is good!** No major issues found.")

                        # Comparison chart
                        with st.expander("📈 View All Metrics"):
                            st.write("**Readability Scores:**")
                            for key, value in metrics.items():
                                if isinstance(value, float):
                                    st.write(f"- {key.replace('_', ' ').title()}: {value:.2f}")
                                else:
                                    st.write(f"- {key.replace('_', ' ').title()}: {value:,}")

                    except Exception as e:
                        st.error(f"❌ Analysis error: {e}")
                        import traceback
                        with st.expander("Error details"):
                            st.code(traceback.format_exc())

            elif input_text:
                st.warning("⚠️ Please enter at least 10 characters for analysis")
            else:
                st.info("👆 Enter text above to get started")

    with tab2:
        st.header("About ClearCraft")

        st.write("""
        ## 🎯 What is ClearCraft?

        ClearCraft is a production-grade text clarity and readability enhancement tool.

        ### Lite Version Features (Current)

        - **📊 Readability Analysis** - 10+ industry-standard metrics
        - **📈 Instant Results** - Fast, lightweight analysis
        - **💯 Free Forever** - Runs on Streamlit Cloud free tier

        ### Full Version Features

        Deploy to **HuggingFace Spaces** (free) for:

        - **🤖 AI-Powered Rewriting** - 7 deterministic enhancement modules
        - **🔬 Semantic Similarity** - Neural embeddings to preserve meaning
        - **🎯 Advanced NLP** - spaCy processing
        - **💬 DeepInfra LLM** - Multiple model support (Llama 4, Claude, Qwen)
        - **📝 Citation Preservation** - Protects references, links, code blocks
        - **⚖️ Quality Guardrails** - 92% similarity threshold, 30% max changes

        ### 🚀 Upgrade to Full Version

        **1. Go to HuggingFace Spaces:**
        ```
        https://huggingface.co/new-space
        ```

        **2. Create New Space:**
        - SDK: Streamlit
        - Hardware: CPU basic (free)

        **3. Connect GitHub:**
        ```
        Repository: seblosiv/humanizer
        Branch: claude/clearcraft-humanizer-app-011CUvktJ3WqTF1d715kpMAg
        ```

        **Why HuggingFace?**
        - ✅ Free tier supports ML models
        - ✅ 16GB RAM (vs Streamlit's 1GB)
        - ✅ Designed for AI apps
        - ✅ Better performance

        ### 📚 Documentation

        - [GitHub Repository](https://github.com/seblosiv/humanizer)
        - [HuggingFace Deploy Guide](https://github.com/seblosiv/humanizer/blob/main/HUGGINGFACE_DEPLOY.md)
        - [Full Documentation](https://github.com/seblosiv/humanizer#readme)

        ### ⚖️ Ethical Use

        ClearCraft is designed for legitimate text improvement:
        - ✅ Academic paper clarity
        - ✅ Business documents
        - ✅ Blog posts
        - ✅ Technical documentation

        **NOT for:**
        - ❌ Bypassing AI detection
        - ❌ Academic dishonesty
        - ❌ Deceptive content

        ---

        **Version:** 1.0.0 Lite
        **Platform:** Streamlit Cloud Free Tier
        **Full Version:** Deploy to HuggingFace Spaces
        """)

        st.divider()
        st.caption("Built with ❤️ using Python and Streamlit")


if __name__ == "__main__":
    main()

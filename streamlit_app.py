#!/usr/bin/env python3
"""
ClearCraft Streamlit Application

Web interface for ClearCraft text clarity enhancement tool.
Deployed on Streamlit Cloud.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Download spacy model if not available
def ensure_spacy_model():
    """Ensure spacy model is downloaded."""
    try:
        import spacy
        spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        st.info("📥 Downloading language model (one-time setup)...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        st.success("✅ Language model downloaded successfully!")

# Ensure model is available
ensure_spacy_model()

# Configure page
st.set_page_config(
    page_title="ClearCraft - AI Text Clarity Enhancement",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_models():
    """Load models with caching."""
    try:
        from clearcraft.analysis import TextAnalyzer
        from clearcraft.selector import TextSelector
        from clearcraft.similarity import SimilarityChecker

        analyzer = TextAnalyzer()
        selector = TextSelector(enable_llm=False)  # LLM disabled for public deployment
        similarity_checker = SimilarityChecker()

        return analyzer, selector, similarity_checker
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.info("This may take a moment on first run as models are downloaded...")
        return None, None, None


# Initialize session state
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
    st.session_state.analyzer = None
    st.session_state.selector = None
    st.session_state.similarity_checker = None


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">✨ ClearCraft</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Text Clarity Enhancement</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("About ClearCraft")
        st.write("""
        ClearCraft enhances text clarity using AI while preserving meaning.

        **Features:**
        - 📊 Readability analysis
        - ✍️ Grammar & style improvement
        - 🎯 Jargon simplification
        - 🔄 Active voice conversion
        - 📝 Sentence structure optimization
        """)

        st.divider()

        st.header("⚙️ Settings")

        tone = st.selectbox(
            "Tone",
            options=["neutral", "academic", "conversational"],
            help="Choose the desired writing tone"
        )

        min_length = st.slider(
            "Min Sentence Length",
            min_value=10,
            max_value=20,
            value=14,
            help="Minimum target sentence length"
        )

        max_length = st.slider(
            "Max Sentence Length",
            min_value=18,
            max_value=30,
            value=22,
            help="Maximum target sentence length"
        )

        enable_disclosure = st.checkbox(
            "Add AI Disclosure",
            value=True,
            help="Add a note that AI was used"
        )

        st.divider()

        st.caption("**Ethical AI Tool**")
        st.caption("Designed for legitimate text improvement only.")

    # Main content
    tab1, tab2, tab3 = st.tabs(["✍️ Analyze & Rewrite", "📊 Analyze Only", "ℹ️ About"])

    with tab1:
        st.header("Analyze & Rewrite Text")

        # Load models if not loaded
        if not st.session_state.models_loaded:
            with st.spinner("Loading AI models... This may take a moment on first use."):
                analyzer, selector, similarity_checker = load_models()
                if analyzer and selector:
                    st.session_state.analyzer = analyzer
                    st.session_state.selector = selector
                    st.session_state.similarity_checker = similarity_checker
                    st.session_state.models_loaded = True
                    st.success("✅ Models loaded successfully!")
                else:
                    st.error("Failed to load models. Please refresh the page.")
                    return

        # Text input
        input_text = st.text_area(
            "Enter your text:",
            height=200,
            placeholder="Paste your text here for clarity enhancement...",
            help="Maximum 50,000 characters"
        )

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            analyze_button = st.button("🔍 Analyze", use_container_width=True, type="secondary")

        with col2:
            rewrite_button = st.button("✨ Rewrite", use_container_width=True, type="primary")

        if input_text:
            # Validate input
            if len(input_text) > 50000:
                st.error("❌ Text too long. Maximum 50,000 characters.")
                return

            if len(input_text) < 10:
                st.warning("⚠️ Text too short. Please enter at least 10 characters.")
                return

            # Analysis
            if analyze_button:
                with st.spinner("Analyzing text..."):
                    try:
                        analysis = st.session_state.analyzer.analyze(input_text)

                        st.success("✅ Analysis complete!")

                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Flesch Reading Ease", f"{analysis.metrics.flesch_reading_ease:.1f}")
                            st.caption("Higher is easier (0-100)")

                        with col2:
                            st.metric("Grade Level", f"{analysis.metrics.flesch_kincaid_grade:.1f}")
                            st.caption("U.S. school grade")

                        with col3:
                            st.metric("Passive Voice", f"{analysis.metrics.passive_ratio:.1%}")
                            st.caption("Lower is better")

                        with col4:
                            st.metric("Word Count", f"{analysis.metrics.total_words:,}")
                            st.caption(f"{analysis.metrics.sentence_count} sentences")

                        # Additional metrics
                        with st.expander("📈 Detailed Metrics"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write("**Readability:**")
                                st.write(f"- Gunning Fog: {analysis.metrics.gunning_fog:.1f}")
                                st.write(f"- SMOG Index: {analysis.metrics.smog_index:.1f}")
                                st.write(f"- Avg Sentence Length: {analysis.metrics.avg_sentence_length:.1f}")

                            with col2:
                                st.write("**Language Quality:**")
                                st.write(f"- Lexical Diversity (TTR): {analysis.metrics.ttr:.2f}")
                                if analysis.metrics.mtld:
                                    st.write(f"- MTLD: {analysis.metrics.mtld:.1f}")
                                st.write(f"- Repetition Ratio: {analysis.metrics.repetition_ratio:.1%}")

                        # Issues found
                        issues = []
                        if analysis.metrics.flesch_reading_ease < 60:
                            issues.append("Low readability (Flesch < 60)")
                        if analysis.metrics.passive_ratio > 0.15:
                            issues.append(f"High passive voice ({analysis.metrics.passive_ratio:.1%})")
                        if analysis.metrics.avg_sentence_length > 25:
                            issues.append("Sentences too long")
                        if analysis.metrics.repetition_ratio > 0.10:
                            issues.append("High repetition")

                        if issues:
                            st.warning("**Issues Found:**")
                            for issue in issues:
                                st.write(f"- {issue}")
                        else:
                            st.success("✅ No major issues found!")

                    except Exception as e:
                        st.error(f"❌ Analysis error: {e}")

            # Rewriting
            if rewrite_button:
                with st.spinner("Rewriting text... This may take 10-30 seconds."):
                    try:
                        start_time = time.time()

                        # Update selector settings
                        st.session_state.selector.target_avg_sentence_length = (min_length, max_length)

                        # Rewrite
                        result = st.session_state.selector.rewrite(
                            text=input_text,
                            tone=tone,
                            enable_disclosure=enable_disclosure
                        )

                        duration = time.time() - start_time

                        st.success(f"✅ Rewriting complete! ({duration:.1f}s)")

                        # Show results
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Original Text")
                            st.text_area(
                                "Original",
                                value=result.original_text,
                                height=300,
                                disabled=True,
                                label_visibility="collapsed"
                            )

                            st.write("**Original Metrics:**")
                            st.write(f"- Flesch: {result.original_metrics.flesch_reading_ease:.1f}")
                            st.write(f"- Passive: {result.original_metrics.passive_ratio:.1%}")
                            st.write(f"- Avg Sentence: {result.original_metrics.avg_sentence_length:.1f}")

                        with col2:
                            st.subheader("Improved Text")
                            st.text_area(
                                "Improved",
                                value=result.rewritten_text,
                                height=300,
                                disabled=True,
                                label_visibility="collapsed"
                            )

                            st.write("**Improved Metrics:**")
                            st.write(f"- Flesch: {result.rewritten_metrics.flesch_reading_ease:.1f}")
                            improvement = result.rewritten_metrics.flesch_reading_ease - result.original_metrics.flesch_reading_ease
                            if improvement > 0:
                                st.write(f"  ↑ +{improvement:.1f} improvement")

                            st.write(f"- Passive: {result.rewritten_metrics.passive_ratio:.1%}")
                            passive_improvement = result.original_metrics.passive_ratio - result.rewritten_metrics.passive_ratio
                            if passive_improvement > 0:
                                st.write(f"  ↓ -{passive_improvement:.1%} reduction")

                            st.write(f"- Avg Sentence: {result.rewritten_metrics.avg_sentence_length:.1f}")

                        # Quality metrics
                        st.divider()

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Semantic Similarity",
                                f"{result.overall_similarity:.1%}",
                                help="How well meaning is preserved (higher is better)"
                            )

                        with col2:
                            st.metric(
                                "Change Ratio",
                                f"{result.total_change_ratio:.1%}",
                                help="How much text was modified"
                            )

                        with col3:
                            st.metric(
                                "Transformations",
                                f"{len(result.change_operations)}",
                                help="Number of improvements applied"
                            )

                        # Download button
                        st.download_button(
                            label="📥 Download Improved Text",
                            data=result.rewritten_text,
                            file_name="clearcraft_improved.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                        # Changes applied
                        with st.expander("🔍 View Changes Applied"):
                            if result.change_operations:
                                for i, op in enumerate(result.change_operations[:10], 1):  # Show first 10
                                    st.write(f"{i}. **{op.operation}** (confidence: {op.confidence:.1%})")
                                    if op.old_text and op.new_text:
                                        st.write(f"   - Before: `{op.old_text[:100]}`")
                                        st.write(f"   - After: `{op.new_text[:100]}`")

                                if len(result.change_operations) > 10:
                                    st.caption(f"... and {len(result.change_operations) - 10} more changes")
                            else:
                                st.write("No changes applied.")

                    except Exception as e:
                        st.error(f"❌ Rewriting error: {e}")
                        import traceback
                        with st.expander("Error details"):
                            st.code(traceback.format_exc())

        else:
            st.info("👆 Enter text above to get started")

    with tab2:
        st.header("Analyze Text Only")

        # Load models if not loaded
        if not st.session_state.models_loaded:
            with st.spinner("Loading AI models..."):
                analyzer, selector, similarity_checker = load_models()
                if analyzer:
                    st.session_state.analyzer = analyzer
                    st.session_state.selector = selector
                    st.session_state.similarity_checker = similarity_checker
                    st.session_state.models_loaded = True

        analyze_text = st.text_area(
            "Enter text to analyze:",
            height=200,
            placeholder="Paste your text here for readability analysis...",
            key="analyze_only"
        )

        if st.button("🔍 Analyze", key="analyze_only_btn", use_container_width=True):
            if analyze_text and len(analyze_text) >= 10:
                with st.spinner("Analyzing..."):
                    try:
                        analysis = st.session_state.analyzer.analyze(analyze_text)

                        # Metrics grid
                        st.subheader("📊 Readability Metrics")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Flesch Reading Ease", f"{analysis.metrics.flesch_reading_ease:.1f}")
                            if analysis.metrics.flesch_reading_ease >= 80:
                                st.caption("🟢 Very Easy")
                            elif analysis.metrics.flesch_reading_ease >= 60:
                                st.caption("🟡 Easy")
                            elif analysis.metrics.flesch_reading_ease >= 50:
                                st.caption("🟠 Moderate")
                            else:
                                st.caption("🔴 Difficult")

                        with col2:
                            st.metric("Grade Level", f"{analysis.metrics.flesch_kincaid_grade:.1f}")
                            st.caption(f"U.S. Grade {analysis.metrics.flesch_kincaid_grade:.0f}")

                        with col3:
                            st.metric("Gunning Fog", f"{analysis.metrics.gunning_fog:.1f}")
                            st.caption("Years of education needed")

                        st.divider()

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Word Count", f"{analysis.metrics.total_words:,}")
                            st.caption(f"{analysis.metrics.sentence_count} sentences")

                        with col2:
                            st.metric("Avg Sentence Length", f"{analysis.metrics.avg_sentence_length:.1f}")
                            if 14 <= analysis.metrics.avg_sentence_length <= 22:
                                st.caption("🟢 Optimal")
                            else:
                                st.caption("🟡 Could be improved")

                        with col3:
                            st.metric("Passive Voice", f"{analysis.metrics.passive_ratio:.1%}")
                            if analysis.metrics.passive_ratio <= 0.15:
                                st.caption("🟢 Good")
                            else:
                                st.caption("🔴 Too high")

                        # Recommendations
                        st.subheader("💡 Recommendations")

                        recommendations = []

                        if analysis.metrics.flesch_reading_ease < 60:
                            recommendations.append("📖 Improve readability - text is difficult to read")

                        if analysis.metrics.avg_sentence_length > 25:
                            recommendations.append("✂️ Shorten sentences - average length is too high")

                        if analysis.metrics.passive_ratio > 0.15:
                            recommendations.append("🎯 Reduce passive voice - use more active constructions")

                        if analysis.metrics.repetition_ratio > 0.10:
                            recommendations.append("🔄 Vary language - reduce repetitive phrases")

                        if analysis.metrics.gunning_fog > 15:
                            recommendations.append("🎓 Simplify vocabulary - text requires college-level education")

                        if recommendations:
                            for rec in recommendations:
                                st.write(f"- {rec}")
                        else:
                            st.success("✅ Text quality is good! No major issues found.")

                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter at least 10 characters")

    with tab3:
        st.header("About ClearCraft")

        st.write("""
        ClearCraft is a production-grade, ethical AI tool for enhancing text clarity.

        ### 🎯 What It Does

        - **Analyzes** text readability using scientific metrics
        - **Rewrites** text to improve clarity while preserving meaning
        - **Simplifies** jargon and complex language
        - **Converts** passive voice to active
        - **Optimizes** sentence structure

        ### ✅ Key Features

        - **Semantic Similarity**: Ensures rewritten text preserves original meaning (>92% similarity)
        - **Quality Guardrails**: Maximum 30% change ratio to preserve author's voice
        - **Citation Preservation**: Protects academic citations, code blocks, and links
        - **Transparency**: Optional disclosure that AI was used
        - **Ethical Design**: Built-in safeguards against misuse

        ### 🔧 Technology

        - **NLP Models**: spaCy, sentence-transformers
        - **Readability Metrics**: Flesch Reading Ease, Gunning Fog, SMOG, MTLD
        - **Deterministic Rewriters**: 7 specialized text enhancement modules
        - **Python Stack**: FastAPI, Pydantic, PyTorch

        ### 📊 Use Cases

        - Academic paper clarity improvement
        - Business document simplification
        - Blog post readability enhancement
        - Technical documentation clarification
        - General writing improvement

        ### ⚖️ Ethical Considerations

        ClearCraft is designed for **legitimate text improvement only**, not for:
        - Bypassing AI detection systems
        - Academic dishonesty
        - Generating deceptive content
        - Evading content filters

        ### 📚 Learn More

        - [GitHub Repository](https://github.com/yourorg/clearcraft)
        - [Documentation](https://github.com/yourorg/clearcraft#readme)
        - [Research Methods](https://github.com/yourorg/clearcraft/blob/main/METHODS.md)

        ### 📝 License

        MIT License with Ethical Use Notice

        ---

        **Version:** 1.0.0
        **Last Updated:** 2025-01-08
        """)

        st.divider()

        st.caption("Built with ❤️ using Python, FastAPI, and Streamlit")


if __name__ == "__main__":
    main()

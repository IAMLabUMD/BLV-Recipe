"""
API Configuration Guide for the Recipe Pipeline

This guide explains how to easily switch between different LLM providers
(Groq, Anthropic) across your pipeline steps.

Table of Contents:
1. Quick Start
2. Setup & Requirements
3. Configuration Methods
4. Advanced Configuration
5. Troubleshooting
"""

# ============================================================================
# 1. QUICK START
# ============================================================================
"""
To switch from Groq to Claude Sonnet 3.5:

1. Make sure ANTHROPIC_API_KEY is in your .env file
2. Add this to run_pipeline.py (top of the main function):

    from config import LLMConfig, LLMProvider, MODELS

    # Switch all steps to Claude Sonnet 3.5
    LLMConfig.set_all_steps(
        provider=LLMProvider.ANTHROPIC,
        model=MODELS["claude-sonnet-3.5"],
    )

3. Run your pipeline as normal

That's it! All steps will now use Claude Sonnet 3.5 instead of Groq.
"""

# ============================================================================
# 2. SETUP & REQUIREMENTS
# ============================================================================
"""
A. Update your .env file

Add your API keys. You only need to add the ones for providers you'll use:

    # For Groq
    GROQ_API_KEY=your_groq_api_key_here

    # For Anthropic (Claude)
    ANTHROPIC_API_KEY=your_anthropic_api_key_here

B. Install dependencies

If using Anthropic (Claude), make sure anthropic is in requirements.txt.
It's already included. Install it with:

    pip install -r requirements.txt

C. Files included in this system

    config.py          - Configuration management
    llm_client.py      - Unified LLM client (handles all providers)
    examples_config.py - Examples of how to configure
"""

# ============================================================================
# 3. CONFIGURATION METHODS
# ============================================================================
"""
There are three main ways to configure your pipeline:

METHOD 1: Switch all steps at once (Recommended)
────────────────────────────────────────────────

This is the simplest approach:

    from config import LLMConfig, LLMProvider, MODELS

    # Use Claude for everything
    LLMConfig.set_all_steps(
        provider=LLMProvider.ANTHROPIC,
        model=MODELS["claude-sonnet-3.5"],
    )

Common model aliases:

    Groq models:
    - MODELS["llama-3.3-70b"]
    - MODELS["llama-3.1-70b"]
    - MODELS["mixtral-8x7b"]

    Anthropic models:
    - MODELS["claude-sonnet-3.5"]  # Recommended
    - MODELS["claude-opus"]
    - MODELS["claude-haiku"]


METHOD 2: Configure individual steps
──────────────────────────────────────

If you want different APIs for different steps:

    from config import LLMConfig, LLMProvider, MODELS

    # Step 2 uses Claude
    LLMConfig.set_step_config(
        "step2_adapt_recipe",
        provider=LLMProvider.ANTHROPIC,
        model=MODELS["claude-sonnet-3.5"],
    )

    # Step 3 uses Groq (cheaper/faster)
    LLMConfig.set_step_config(
        "step3_handle_tools",
        provider=LLMProvider.GROQ,
        model=MODELS["llama-3.3-70b"],
    )

    # Other steps use default
    # (see config.py for which steps exist)

Available step names:
    - step2_adapt_recipe
    - step3_handle_tools
    - step4_detect_visual_cues
    - step5_replace_visual_cues
    - step6_to_accessible_html
    - step7_add_tool_links


METHOD 3: Use programmatic configuration in run_pipeline.py
────────────────────────────────────────────────────────────

Add this to your run_pipeline.py main() function:

    def main():
        # Configure LLM before running any steps
        from config import LLMConfig, LLMProvider, MODELS
        LLMConfig.set_all_steps(
            provider=LLMProvider.ANTHROPIC,
            model=MODELS["claude-sonnet-3.5"],
        )

        # Now run your pipeline steps...
        # step2 = run_step2(...)
        # step3 = run_step3(step2, ...)
        # etc.
"""

# ============================================================================
# 4. ADVANCED CONFIGURATION
# ============================================================================
"""
A. Using custom model names

If you want to use a model not in the MODELS dict:

    from config import LLMConfig, LLMProvider

    LLMConfig.set_all_steps(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-opus-20240229",  # Use any model name
    )

See provider documentation for available models.


B. Creating a config file

For complex configurations, create a separate config file:

    # my_pipeline_config.py
    from config import LLMConfig, LLMProvider, MODELS

    def setup_production():
        \"\"\"Production: Use Claude for quality.\"\"\"
        LLMConfig.set_all_steps(
            provider=LLMProvider.ANTHROPIC,
            model=MODELS["claude-sonnet-3.5"],
        )

    def setup_development():
        \"\"\"Development: Use fast/cheap Groq.\"\"\"
        LLMConfig.set_all_steps(
            provider=LLMProvider.GROQ,
            model=MODELS["llama-3.3-70b"],
        )

    def setup_testing():
        \"\"\"Testing: Mix of fast and quality.\"\"\"
        # Custom setup for testing...

Then in run_pipeline.py:

    from my_pipeline_config import setup_production

    def main():
        setup_production()
        # Run pipeline...


C. Environment-based configuration

    import os
    from config import LLMConfig, LLMProvider, MODELS

    env = os.getenv("PIPELINE_ENV", "development")

    if env == "production":
        LLMConfig.set_all_steps(
            provider=LLMProvider.ANTHROPIC,
            model=MODELS["claude-sonnet-3.5"],
        )
    else:
        LLMConfig.set_all_steps(
            provider=LLMProvider.GROQ,
            model=MODELS["llama-3.3-70b"],
        )
"""

# ============================================================================
# 5. TROUBLESHOOTING
# ============================================================================
"""
Q: I get "GROQ_API_KEY not set in .env"
A: Add GROQ_API_KEY to your .env file, or if using Anthropic,
   make sure you're setting the config to use Anthropic.

Q: I get "ANTHROPIC_API_KEY not set in .env"
A: Add ANTHROPIC_API_KEY to your .env file.

Q: My code still uses the old Groq import
A: The pipeline files have been updated. If you have custom code,
   use LLMClient.from_step_name("step_name") instead:

   OLD: from groq import Groq; client = Groq(api_key=...)
   NEW: from llm_client import LLMClient; client = LLMClient.from_step_name("step2")

Q: How do I check what's currently configured?
A: Run this:

   from config import LLMConfig
   print(LLMConfig.STEP_CONFIGS)

Q: Can I use a different model mid-pipeline?
A: Yes! Just reconfigure before calling a step:

   from config import LLMConfig, LLMProvider, MODELS

   # Run step 2 with Claude
   LLMConfig.set_step_config("step2_adapt_recipe",
                             LLMProvider.ANTHROPIC, MODELS["claude-sonnet-3.5"])
   output2 = run_step2(input_file)

   # Switch to Groq for step 3
   LLMConfig.set_step_config("step3_handle_tools",
                             LLMProvider.GROQ, MODELS["llama-3.3-70b"])
   output3 = run_step3(output2)

Q: Which provider is best?
A:
   - Claude Sonnet 3.5 (Anthropic): Better quality, good for recipe adaptation
   - Llama 3.3 70B (Groq): Very fast, cheaper, good for structured tasks
   - Mixtral 8x7B (Groq): Fast, good balance of quality and speed
"""

print(__doc__)

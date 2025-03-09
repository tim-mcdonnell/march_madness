# Documentation Guide

This guide outlines the documentation system for the NCAA March Madness Predictor project, providing standards and procedures for maintaining and extending our documentation.

## Documentation Structure

Our documentation follows a structured organization designed to serve different audiences and purposes:

```
docs/
├── index.md                    # Main documentation entry point
├── features/                   # Feature system documentation
│   ├── index.md                # Feature system overview
│   ├── reference/              # Feature technical reference
│   │   └── overview.md         # Complete feature catalog
│   ├── team_performance/       # Team performance feature docs
│   └── shooting/               # Shooting feature docs
├── data/                       # Data documentation
│   ├── index.md                # Data system overview
│   ├── reference/              # Technical reference for data
│   │   ├── schema.md           # Data schemas
│   │   ├── validation.md       # Data validation rules
│   │   └── directory_structure.md # File/directory organization
│   └── processing.md           # Data processing principles
├── pipeline/                   # Pipeline documentation
│   ├── index.md                # Pipeline overview
│   ├── cli.md                  # Command-line interface
│   └── stages/                 # Documentation for pipeline stages
├── developer/                  # Developer documentation
│   ├── index.md                # Developer guide overview
│   ├── getting_started.md      # Onboarding guide
│   ├── ai_assistant_guide.md   # Guide for AI assistants
│   ├── documentation_guide.md  # This guide
│   ├── coding_standards.md     # Code style and standards
│   └── examples/               # Usage examples
├── templates/                  # Documentation templates
│   ├── feature_doc.md          # Template for feature documentation
│   └── analysis_report.md      # Template for analysis reports
└── research/                   # Reference materials for methodology
```

## Documentation Standards

### File Naming and Organization

1. **File Naming**:
   - Use lowercase for all file and directory names
   - Use underscores to separate words in filenames
   - Every directory should have an `index.md` as its entry point

2. **Directory Organization**:
   - Group related documentation together in directories
   - Use subdirectories for specific features, categories, or topics
   - Limit directory nesting to 3 levels where possible

### Content Standards

1. **Document Structure**:
   - Each document should have a single, descriptive H1 title
   - Use a logical hierarchy of H2, H3, etc. for sections
   - Include a brief introduction/overview at the beginning
   - Include a table of contents for longer documents (>1000 words)

2. **Markdown Formatting**:
   - Use Markdown formatting consistently
   - Code blocks should specify the language for proper syntax highlighting
   - Use tables for structured data
   - Use numbered lists for sequential steps
   - Use bullet points for unordered lists

3. **Cross-Referencing**:
   - Use relative links to reference other documentation files
   - Include "Related Documentation" sections where appropriate
   - Avoid hardcoded URLs to internal documentation

## Feature Documentation

All implemented features must have proper documentation following our standardized format:

1. **Documentation Location**: `docs/features/{category}/{ID}_{feature_name}.md`

2. **Required Sections**:
   - Overview (category, complexity, status)
   - Description (what the feature measures)
   - Implementation (link to source code)
   - Formula/Calculation (mathematical formula and code explanation)
   - Data Requirements (input data and required columns)
   - Implementation Notes (considerations, edge cases, optimizations)
   - Interpretation (typical range, benchmark values, context)
   - Usage Examples (code examples)
   - Visualization (recommended visualization approaches)
   - Related Features (connections to other features)
   - Version History (implementation changes)

3. **Feature Registry**: 
   - Feature details should be added to `features/reference/overview.md`
   - Do not maintain duplicate feature lists

## Data Documentation

Data documentation is centralized in the `docs/data/` directory:

1. **Schema Documentation**:
   - Document all data files, their structure, and relationships
   - Include column names, data types, and descriptions
   - List example values where helpful

2. **Processing Documentation**:
   - Document data cleaning and transformation procedures
   - Explain validation rules and handling of edge cases
   - Document any assumptions made during processing

## Documentation for AI Assistants

When documenting code for AI assistant interaction:

1. **AI-Friendly Patterns**:
   - Include comprehensive docstrings on all functions and classes
   - Provide clear examples in documentation
   - Use type hints consistently
   - Document expected inputs/outputs and edge cases

2. **Context Enhancement**:
   - Include "why" explanations, not just "what" descriptions
   - Document relationships between components
   - Highlight important patterns and architectural decisions

## Documentation Maintenance

1. **Update Cycles**:
   - Update documentation alongside code changes
   - Review documentation completeness before each PR
   - Perform a comprehensive documentation review monthly

2. **Quality Assurance**:
   - Ensure all links work
   - Check for outdated information
   - Verify examples still work with current code

## Templates

Use our standardized templates when creating new documentation:

1. **Feature Documentation**: Use `templates/feature_doc.md`
2. **Analysis Reports**: Use `templates/analysis_report.md`

Following these templates ensures consistency and completeness across our documentation.

## Contributing to Documentation

1. **Adding New Documentation**:
   - Identify the appropriate location in the structure
   - Use existing templates where available
   - Follow the standards outlined in this guide
   - Update relevant index.md files to include your new content

2. **Updating Existing Documentation**:
   - Maintain the existing structure and formatting
   - Update all affected documentation when making changes
   - Add to the version history if applicable
   - Consider impacts on cross-references

## Documentation Philosophy

Our documentation follows these core principles:

1. **DRY (Don't Repeat Yourself)**: 
   - Information should exist in exactly one place
   - Use cross-references rather than duplication

2. **Progressive Disclosure**:
   - Start with high-level overviews
   - Provide paths to more detailed information
   - Allow users to dive deeper as needed

3. **Audience Awareness**:
   - Consider the technical level of the intended audience
   - Provide appropriate context for different users
   - Use consistent terminology throughout

4. **Maintenance Focused**:
   - Design documentation to be easy to maintain
   - Prefer automated documentation where possible
   - Keep documentation close to the code it describes 
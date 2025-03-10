# Documentation Standards

This document outlines the standards for creating and maintaining documentation in the NCAA March Madness Predictor project.

## 1. Documentation Types

| Category | Description | Location | Audience |
|----------|-------------|----------|----------|
| **Getting Started** | Onboarding and setup | `docs/guides/` | New developers |
| **Usage** | Using the system | `docs/usage/` | End users |
| **Architecture** | System design and structure | Root `/README.md` and `docs/architecture/` | All developers |
| **Principles** | Core development principles | `docs/PRINCIPLES.md` | All developers |
| **Standards** | Specific standards for code, testing, etc. | `docs/standards/` | All developers |
| **Guides** | Step-by-step instructions | `docs/guides/` | Developers performing specific tasks |
| **Component** | Details of specific components | `docs/components/` | Developers working on specific components |
| **Feature** | Details of prediction features | `docs/components/features/` | Feature developers |
| **Reference** | Technical reference information | `docs/reference/` | Developers needing specific details |
| **API Reference** | Component interfaces | `docs/reference/api/` | Developers |
| **Schema** | Data structure documentation | `docs/reference/schema/` | Developers working with data |
| **Development** | Development workflows | `docs/guides/` | Contributors |

## 2. Documentation Quality Criteria

All documentation must meet these criteria:

### 2.1 Completeness
- Covers all aspects of the subject
- Includes all necessary information for the target audience
- No important details are omitted

### 2.2 Accuracy
- Reflects current implementation
- No outdated information
- All examples work as documented

### 2.3 Clarity
- Clear language with minimal jargon
- Well-structured with logical flow
- Appropriate use of formatting (headings, lists, etc.)

### 2.4 Actionability
- Provides enough information to take action
- Includes examples where appropriate
- Explains why, not just what

### 2.5 Maintainability
- Structured for easy updates
- Cross-references related documentation
- Version-aligned with code

## 3. Documentation Structure Requirements

### 3.1 Required Sections for All Documents

- **Title**: Clear, descriptive title
- **Overview/Introduction**: Brief introduction to the document purpose
- **Main Content**: The primary content, organized logically
- **Related Resources**: Links to related documentation or resources

### 3.2 Component Documentation Requirements

All component documentation must include:

- **Purpose**: What problem does the component solve?
- **Architecture**: How is the component designed?
- **Interface**: How do other components interact with it?
- **Usage**: How is the component used?
- **Examples**: Examples of common usage
- **Dependencies**: What other components does it depend on?
- **Implementation Details**: Key implementation aspects
- **Testing**: How to test the component

### 3.3 Feature Documentation Requirements

All feature documentation must include:

- **ID and Name**: Feature ID and name from FEATURES.md
- **Definition**: Mathematical or logical definition
- **Implementation**: How it's calculated
- **Dependencies**: What other features or data it depends on
- **Input Requirements**: Required data for calculation
- **Output Schema**: Structure of the output
- **Data Quality Aspects**: Quality considerations
- **Edge Cases**: Special cases to consider

## 4. Style Guidelines

### 4.1 Formatting

- Use Markdown for all documentation
- Follow a consistent heading structure (# for title, ## for sections, etc.)
- Use code blocks with language specification for code examples
- Use tables for structured information
- Use lists for sequential or unordered items

### 4.2 Writing Style

- Use active voice
- Be concise but complete
- Use consistent terminology
- Define acronyms and technical terms on first use
- Use present tense

### 4.3 Links and References

- Use relative links for internal documentation
- Use descriptive link text
- Include version information for external references
- Avoid breaking links by updating references when files move

## 5. Documentation Creation Process

### 5.1 New Documentation Workflow

1. **Identify Need**: Determine what needs to be documented
2. **Select Template**: Use the appropriate template from `docs/standards/templates/`
3. **Create Draft**: Write the initial documentation
4. **Review**: Have someone else review the documentation
5. **Finalize**: Incorporate feedback and finalize
6. **Publish**: Add to the repository and update any references

### 5.2 Documentation Update Workflow

1. **Identify Change**: Determine what needs to be updated
2. **Update Documentation**: Make the necessary changes
3. **Review Changes**: Have someone review the changes
4. **Finalize**: Incorporate feedback and finalize
5. **Publish**: Commit changes and update any references

## 6. Documentation Templates

Templates for different documentation types are available in `docs/standards/templates/`:

- [Component Documentation Template](templates/component_doc.md)
- [Feature Documentation Template](templates/feature_doc.md)
- [Guide Template](templates/guide.md)
- [Standard Template](templates/standard.md)

## 7. Documentation Review Checklist

Use this checklist when reviewing documentation:

- [ ] Follows the appropriate template
- [ ] Meets completeness criteria
- [ ] Information is accurate and up-to-date
- [ ] Writing is clear and concise
- [ ] Includes appropriate examples
- [ ] Links to related documentation
- [ ] No broken links
- [ ] No spelling or grammatical errors
- [ ] Formatted consistently
- [ ] Appropriately placed in the documentation structure

## 8. Integration with Code

### 8.1 Code-to-Doc References

Include references to documentation in code comments:

```python
def calculate_win_percentage(games_df):
    """
    Calculate team win percentages.
    
    See docs/components/features/T01_win_percentage.md for details.
    """
```

### 8.2 Doc-to-Code References

Include references to code in documentation:

```markdown
# Win Percentage Feature

This feature is implemented in:
- [`src/features/team_performance/win_percentage.py`](../../../src/features/team_performance/win_percentage.py)
```

## 9. Documentation Maintenance

### 9.1 Regular Review

- Documentation should be reviewed every 6 months
- Documentation should be updated whenever related code changes
- Documentation issues should be tracked in the issue tracker

### 9.2 Version Alignment

- Documentation version should align with code version
- Note when documentation applies to specific versions only 
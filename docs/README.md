# NCAA March Madness Predictor Documentation

## Introduction

This is the central documentation hub for the NCAA March Madness Predictor project. This documentation is organized to be both comprehensive and easily navigable, with clear paths for different use cases.

## Quick Links

- [Architecture Overview](../README.md)
- [Development Principles](PRINCIPLES.md)
- [Development Workflow](guides/development_workflow.md)
- [Feature Creation Guide](guides/feature_creation.md)

## Documentation By Role

### For New Developers
1. [Project Overview](../README.md) - Start here for a high-level understanding
2. [Development Environment Setup](guides/setup.md) - How to set up your local environment
3. [Development Workflow](guides/development_workflow.md) - Our development process

### For Feature Developers
1. [Feature Development Guide](guides/feature_creation.md) - How to create new prediction features
2. [Feature Standards](standards/feature_standards.md) - Standards for feature implementation
3. [Feature Testing Guide](guides/testing_guide.md) - How to test features thoroughly

### For System Developers
1. [Component Standards](standards/component_standards.md) - Standards for system components
2. [API Client Documentation](components/api_client/README.md) - ESPN API client details
3. [Database Documentation](components/database/README.md) - DuckDB implementation details

## Documentation By Topic

- **Architecture**: [System Architecture](../README.md)
- **Standards**: [Coding](standards/coding_standards.md) | [Testing](standards/testing_standards.md) | [Documentation](standards/doc_standards.md)
- **Components**: [API Client](components/api_client/README.md) | [Database](components/database/README.md) | [Feature System](components/features/README.md)
- **Reference**: [Data Schema](reference/schema/README.md) | [API Reference](reference/api/README.md)

## Documentation Structure

Our documentation is organized as follows:

```
docs/
├── README.md                 # This file - documentation home
├── PRINCIPLES.md             # Core development principles
├── standards/                # All standards in one location
│   ├── coding_standards.md   # Coding conventions
│   ├── testing_standards.md  # Testing requirements
│   ├── doc_standards.md      # Documentation requirements
│   └── templates/            # Reusable templates
├── guides/                   # How-to guides
│   ├── development_workflow.md  # Development process
│   ├── feature_creation.md   # Creating new features
│   └── testing_guide.md      # How to test effectively
├── components/               # Component-specific documentation
│   ├── api_client/           # API client documentation
│   ├── database/             # Database documentation
│   └── features/             # Feature system documentation
└── reference/                # Technical reference
    ├── schema/               # Data schemas
    ├── api/                  # API reference
    └── examples/             # Code examples
```

## Contribution Guidelines

When contributing to documentation:

1. Follow the [Documentation Standards](standards/doc_standards.md)
2. Use the appropriate [template](standards/templates/) for new documentation
3. Update the main README (this file) if adding new sections
4. Ensure all links work correctly
5. Keep documentation synchronized with code changes 
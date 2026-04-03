# Architecture Diagrams

This directory contains all architectural diagrams for the storytelling platform.

## Directory Structure

```
diagrams/
├── source/           # Mermaid source files (.mmd)
├── exports/          # Exported diagram files (PNG, SVG, PDF)
├── templates/        # Diagram templates and standards
└── README.md         # This file
```

## Diagram Categories

### System Architecture
- `system-overview.mmd` - High-level system architecture
- `deployment-architecture.mmd` - Azure deployment architecture
- `component-interaction.mmd` - Component interaction flows

### Data Architecture
- `entity-relationship.mmd` - Complete ER diagram
- `data-flow.mmd` - Data flow diagrams
- `database-schema.mmd` - Database schema overview

### Service Architecture
- `ai-services.mmd` - AI services integration
- `authentication-flow.mmd` - Authentication and authorization flows
- `api-architecture.mmd` - API structure and organization

## Export Instructions

### Using Mermaid CLI
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Export to PNG
mmdc -i source/system-overview.mmd -o exports/system-overview.png

# Export to PDF
mmdc -i source/system-overview.mmd -o exports/system-overview.pdf

# Export to SVG
mmdc -i source/system-overview.mmd -o exports/system-overview.svg
```

### Using Online Tools
1. Copy diagram source from `.mmd` files
2. Paste into [Mermaid Live Editor](https://mermaid.live/)
3. Export in desired format

### Batch Export Script
```bash
#!/bin/bash
# Export all diagrams
for file in source/*.mmd; do
    filename=$(basename "$file" .mmd)
    mmdc -i "$file" -o "exports/${filename}.png"
    mmdc -i "$file" -o "exports/${filename}.pdf"
done
```

## Diagram Standards

### Styling Guidelines
- Use consistent color schemes across all diagrams
- Include descriptive titles and legends
- Keep diagrams readable at standard document sizes
- Use standard UML notation where applicable

### Naming Conventions
- Use kebab-case for file names
- Include version numbers for major changes
- Use descriptive names that indicate diagram purpose

## Maintenance

- Update diagrams when architecture changes
- Maintain both source and exported versions
- Test diagram exports regularly
- Keep this README updated with new diagram categories
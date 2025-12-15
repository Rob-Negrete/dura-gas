# Contributing to DuraGas

Thank you for your interest in contributing to DuraGas!

## Getting Started

### Prerequisites
- Python 3.12+
- Home Assistant development environment
- Git

### Setup
1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt
```

## Development Guidelines

### Code Style
- Use full type hints on all functions
- Follow Home Assistant coding standards
- Use async/await for all I/O operations
- Keep calculations in `coordinator.py`

### Testing
Run tests before submitting:
```bash
pytest tests/
```

### Translations
- English strings go in `strings.json` and `translations/en.json`
- Spanish translations in `translations/es.json`
- Use Mexican Spanish with informal "tú" form

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests if applicable
4. Update documentation if needed
5. Submit a pull request

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Type hints are complete
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Translations added (if new strings)

## Architecture Notes

### File Responsibilities
- `coordinator.py` - Business logic, calculations, storage
- `sensor.py` / `binary_sensor.py` - Entity definitions only
- `config_flow.py` - Configuration UI
- `const.py` - Constants and enums

### Adding Features

#### New Sensor
1. Add `DuraGasSensorEntityDescription` to `sensor.py`
2. Add translation keys to all JSON files
3. Update coordinator if new calculation needed

#### New Service
1. Define schema in `__init__.py`
2. Create handler function
3. Register service
4. Update `services.yaml`
5. Add translations

## Questions?

Open an issue on GitHub or contact the maintainers.

## Code of Conduct

Be respectful and constructive in all interactions.

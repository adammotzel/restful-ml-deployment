import yaml

from src.app import app


if __name__ == "__main__":
    specs = app.openapi()
    with open("docs/api_specs.yaml", "w") as file:
        yaml.dump(
            specs, 
            file, 
            default_flow_style=False, 
            indent=2
        )

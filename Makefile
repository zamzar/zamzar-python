.PHONY: up clean sync generate test bump publish

SPEC_REMOTE = https://raw.githubusercontent.com/zamzar/zamzar-spec/main/openapi/spec.yaml
SPEC = spec.yaml
GENERATOR_CMD = docker compose exec codegen \
				java -jar /opt/openapi-generator/modules/openapi-generator-cli/target/openapi-generator-cli.jar
GENERATE_ARGS = generate -i $(SPEC) -g python -c openapi-generator-config.yaml
EXEC_CMD = docker compose exec python

up:
	@docker compose up -d

clean:
	@while read -r generated; do rm -f "$$generated" || true; done < .openapi-generator/FILES
	@rm -rf dist

sync:
	@curl -sSL $(SPEC_REMOTE) > $(SPEC)

generate: up
	@$(eval CURRENT_VERSION=$(shell $(EXEC_CMD) python setup.py --version))
	@$(GENERATOR_CMD) $(GENERATE_ARGS) --additional-properties=packageVersion=$(CURRENT_VERSION)
	# Note that the OpenAPI generator currently produces code that can fail the assignment mypy check in some cases;
    # so we add inline comments to ignore these errors
	@sed -i '' -E 's/(for _item in self\.[^:]+:)/\1  # type: ignore[assignment]/g' zamzar/models/*.py

test: up
	@$(EXEC_CMD) mypy
	@$(EXEC_CMD) pytest -rP

build: up
	@$(EXEC_CMD) python -m build

bump: up sync
ifndef VERSION
	$(error VERSION is not set)
endif
	@$(eval CURRENT_VERSION=$(shell $(EXEC_CMD) python setup.py --version))
	@$(EXEC_CMD) sed -i "s/$(CURRENT_VERSION)/$(VERSION)/g" README.md
	@$(EXEC_CMD) sed -i "s/$(CURRENT_VERSION)/$(VERSION)/g" setup.py
	@$(EXEC_CMD) sed -i "s/$(CURRENT_VERSION)/$(VERSION)/g" zamzar/__init__.py
	@$(GENERATOR_CMD) $(GENERATE_ARGS) --additional-properties=packageVersion=$(VERSION)

publish: build
ifndef TWINE_USERNAME
	$(error TWINE_USERNAME is not set)
endif
ifndef TWINE_PASSWORD
	$(error TWINE_PASSWORD is not set)
endif
	@docker compose exec \
		-e TWINE_USERNAME=$(TWINE_USERNAME) \
		-e TWINE_PASSWORD=$(TWINE_PASSWORD) \
		python \
		twine upload --repository testpypi dist/*
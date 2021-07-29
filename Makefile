.PHONY: develop
develop:
	chmod +x develop/make.sh
	./develop/make.sh

# build is responsible for building the project, performing code formats,
# code analysis.
.PHONY: build
build:
	chmod +x develop/build.sh
	./develop/build.sh

.PHONY: test
test:
	chmod +x develop/test.sh
	./develop/test.sh

.PHONY: autogen
autogen:
	python develop/autogen_schema.py
	ychaos manual --file docs/cli/manual.md > /dev/null

# Builds documentation and serves on http://localhost:8000
.PHONY: doc
doc:
	chmod +x develop/doc.sh
	./develop/doc.sh

.PHONY: docbuild
docbuild:
	mkdocs build

.PHONY: schema
schema:
	python3 develop/autogen_schema.py

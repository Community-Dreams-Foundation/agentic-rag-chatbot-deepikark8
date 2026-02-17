.PHONY: sanity install run clean

install:
	pip install -r requirements.txt
	ollama pull llama3.2

run:
	python run.py

sanity:
	@echo "Running sanity check..."
	@mkdir -p artifacts
	@python3 scripts/sanity_test.py

clean:
	rm -rf chroma_db/
	rm -rf memory_store/
	rm -rf artifacts/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	find . -name "*.pyc" -delete

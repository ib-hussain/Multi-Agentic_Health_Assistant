all: compile debug
compile:
		streamlit run website.py
debug: 
# 		streamlit run website.py --logger.level=debug
import solara


@solara.component
def Page():
    with solara.Column(align="center"):
        markdown = """
        ## A Solara Template for Geospatial Applications
        
        ### Introduction

        **A collection of [Solara](https://github.com/widgetti/solara) web apps for geospatial applications.**

        - Web App: <https://cboettig-solara-test.hf.space>
        - GitHub: <https://github.com/boettiger-lab/solara-test>
        - Hugging Face: <https://huggingface.co/spaces/cboettig/solara-test>

        """

        solara.Markdown(markdown)

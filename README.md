# Colin's Resume
### Welcome to my cloud hosted resume!
#### This template can be used to update your self-hosted website, as well as generate a PDF with the same information.
1. The resume information is stored in a YAML file (`resume_builder/resume.yaml`).
    * The YAML schema supports profile-based filtering with `include_in` tags for generating different resume variants (default, technical, leadership)
    * Schema documentation is available in `resume_builder/SCHEMA_DOCUMENTATION.md`
2. The web design is forked from [this repo](https://github.com/afnizarnur/draco). Thank you @draco for the beautiful resume template! Please go sponsor them if you are able and find value in the template like I do.

## Installation
This template uses two main tools to accomplish the conversion to PDF: [Pandoc](https://pandoc.org/) and [wkhtmltopdf](https://wkhtmltopdf.org/). 
1. To install, use the package installer that corresponds to your system. For me, I am doing my code editing on Ubuntu Server  
    ```
    sudo apt install pandoc
    sudo apt install wkhtmltopdf
    ```
    *Thank you to [@vidluther](https://github.com/vidluther) for breaking it down in your [repo](https://github.com/vidluther/markdown-resume). It was a long google-fu road to you.*

2. Update the YAML file at `resume_builder/resume.yaml`. Yes, it is my resume that you are walking all over. Don't worry, I won't be offended.
    - Look to `resume_builder/SCHEMA_DOCUMENTATION.md` for additional fields you can use
    - Use `include_in` tags to control which items appear in different profile variants
    - Available profiles: `default`, `technical`, `leadership`
3. Run the build script in the `resume_builder` folder. The names are all generic so the script can be reused.
    ```bash
    cd resume_builder
    ./build_all.sh                     # Build with default profile
    ./build_all.sh --profile leadership  # Build with specific profile
    ./build_all.sh --all-profiles      # Build all available profiles
    ./build_all.sh --help              # Show all options
    ```
    - This script will do as it says, build all.
        - `index.html` for your website home page
        - `resume.md` to construct the html for the pdf
        - `resume.html` to construct the pdf
        - `resume.pdf` to have a pdf resume!
            - *this will be in the home directory so that it can be accessed quicker online*
        - `output/resume.json` for API/dynamic website loading  

#### From there, you are off to the races!

## Usage Idea
#### This is how my resume is hosted and deployed at [colinmca.com](colinmca.com)
1. The files are stored in an AWS S3 bucket that has been made public.  
    - You can find plenty of tutorials on this online. I think Amazon even has one.
2. CloudFront serves the content and provides SSL encryption so I can have the fancy `s` allowing people to feel all warm and fuzzy while they poke around.
3. Route53 does all the DNS stuff. Boy was that a pain. And I even bought my domain through them!  
4. CodePipeline deploys the content on a successful merge into the `main` branch of this repo. This was surprisingly *easy* to set up and makes life WAAY better.

There are plenty more things I would like to do, but hey isn't that the way things always work? Enjoy!



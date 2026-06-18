import json
import random
import argparse
import pandas as pd
from pathlib import Path


HARD_NEGATIVE_MAPPING = {
    "it": ["data", "operational", "finance"],
    "data": ["it", "finance"],
    "hr": ["pr", "ga"],
    "finance": ["sales", "hr"],
    "creative": ["marketing", "pr"],
    "sales": ["marketing", "cs"],
    "legal": ["hr", "finance"],
    "pr": ["marketing", "creative"],
    "ga": ["hr", "operational"],
    "cs": ["sales", "hr"],
    "operational": ["ga", "finance"]
}


class SyntheticDataGeneratorV2:

    def __init__(self, skills_dir, templates_dir):

        self.skills_dir = Path(skills_dir)
        self.templates_dir = Path(templates_dir)

        self.domains_config = self._load_domain_configs()
        self.templates = self._load_templates()
        self.slot_data = self._prepare_slot_data()

    # =====================================================
    # LOAD CONFIG
    # =====================================================

    def _load_domain_configs(self):

        configs = {}

        for f in self.skills_dir.glob("*.json"):

            with open(
                f,
                "r",
                encoding="utf-8"
            ) as file:

                configs[f.stem.lower()] = json.load(file)

        return configs

    def _load_templates(self):

        templates = {}

        for name in [
            "anchor_templates",
            "positive_templates",
            "negative_templates"
        ]:

            path = self.templates_dir / f"{name}.json"

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                templates[name] = json.load(file)

        return templates

    # =====================================================
    # SLOT DATA
    # =====================================================

    def _prepare_slot_data(self):

        return {

            "company": [
                "Google",
                "Microsoft",
                "Gojek",
                "Tokopedia",
                "Shopee",
                "Traveloka",
                "BCA",
                "Mandiri"
            ],

            "role": [
                "Engineer",
                "Developer",
                "Analyst",
                "Coordinator",
                "Manager",
                "Specialist"
            ],

            "years": [
                "1",
                "2",
                "3",
                "5",
                "7",
                "10"
            ],

            "team": [
                "Engineering",
                "Product",
                "Data",
                "Marketing",
                "Operations",
                "Finance"
            ],

            "project_count": [
                "3",
                "5",
                "10",
                "15"
            ],

            "provider": [
                "AWS",
                "Google Cloud",
                "Microsoft",
                "Coursera",
                "Udemy"
            ]
        }

    # =====================================================
    # TEMPLATE FILLER
    # =====================================================

    def _fill_template(
        self,
        template,
        domain,
        is_positive=True
    ):

        config = self.domains_config.get(
            domain,
            self.domains_config.get("general", {})
        )

        skills = config.get(
            "skills",
            ["Communication"]
        )

        projects = config.get(
            "projects",
            ["Business Project"]
        )

        unrelated_industries = config.get(
            "unrelated_industries",
            ["Agriculture"]
        )

        unrelated_roles = config.get(
            "unrelated_roles",
            ["Operator"]
        )

        unrelated_tools = config.get(
            "unrelated_tools",
            ["Forklift"]
        )

        # skill
        if "{skill}" in template:
            template = template.replace(
                "{skill}",
                random.choice(skills)
            )

        if (
            "{skill1}" in template
            or "{skill2}" in template
        ):

            sampled = random.sample(
                skills,
                min(
                    len(skills),
                    2
                )
            )

            while len(sampled) < 2:
                sampled.append(sampled[0])

            template = template.replace(
                "{skill1}",
                sampled[0]
            )

            template = template.replace(
                "{skill2}",
                sampled[1]
            )

        if "{skill3}" in template:

            template = template.replace(
                "{skill3}",
                random.choice(skills)
            )

        if "{project}" in template:

            template = template.replace(
                "{project}",
                random.choice(projects)
            )

        if "{industry_unrelated}" in template:

            template = template.replace(
                "{industry_unrelated}",
                random.choice(
                    unrelated_industries
                )
            )

        if "{role_unrelated}" in template:

            template = template.replace(
                "{role_unrelated}",
                random.choice(
                    unrelated_roles
                )
            )

        if "{tool_unrelated}" in template:

            template = template.replace(
                "{tool_unrelated}",
                random.choice(
                    unrelated_tools
                )
            )

        for slot, values in self.slot_data.items():

            placeholder = f"{{{slot}}}"

            if placeholder in template:

                template = template.replace(
                    placeholder,
                    random.choice(values)
                )

        if (
            not is_positive
            and "{skill_unrelated}" in template
        ):

            other_domains = [
                d
                for d in self.domains_config.keys()
                if d != domain
            ]

            other_domain = random.choice(
                other_domains
            )

            other_skills = self.domains_config[
                other_domain
            ].get(
                "skills",
                ["Communication"]
            )

            template = template.replace(
                "{skill_unrelated}",
                random.choice(
                    other_skills
                )
            )

        return template

    # =====================================================
    # HARD NEGATIVE
    # =====================================================

    def _get_hard_negative_domain(
        self,
        domain
    ):

        candidates = HARD_NEGATIVE_MAPPING.get(
            domain.lower()
        )

        if candidates:

            valid = [
                d
                for d in candidates
                if d in self.domains_config
            ]

            if valid:
                return random.choice(valid)

        others = [
            d
            for d in self.domains_config.keys()
            if d != domain
        ]

        return random.choice(others)

    # =====================================================
    # MAIN GENERATOR
    # =====================================================

    def generate_triplet_data(
        self,
        num_examples=10000
    ):

        rows = []

        domains = list(
            self.domains_config.keys()
        )

        anchor_templates = self.templates[
            "anchor_templates"
        ]

        positive_templates = self.templates[
            "positive_templates"
        ]

        negative_templates = self.templates[
            "negative_templates"
        ]

        for _ in range(num_examples):

            domain = random.choice(
                domains
            )

            anchor_template = random.choice(
                anchor_templates.get(
                    domain,
                    anchor_templates.get(
                        "general",
                        []
                    )
                )
            )

            positive_template = random.choice(
                positive_templates.get(
                    domain,
                    positive_templates.get(
                        "general",
                        []
                    )
                )
            )

            negative_type = random.choices(
                ["easy", "hard"],
                weights=[30, 70]
            )[0]

            if negative_type == "easy":

                negative_domain = random.choice(
                    [
                        d
                        for d in domains
                        if d != domain
                    ]
                )

            else:

                negative_domain = (
                    self._get_hard_negative_domain(
                        domain
                    )
                )

            negative_template = random.choice(
                negative_templates.get(
                    negative_domain,
                    negative_templates.get(
                        "general",
                        []
                    )
                )
            )

            anchor = self._fill_template(
                anchor_template,
                domain
            )

            positive = self._fill_template(
                positive_template,
                domain,
                is_positive=True
            )

            negative = self._fill_template(
                negative_template,
                negative_domain,
                is_positive=False
            )

            rows.append({

                "anchor": anchor,
                "positive": positive,
                "negative": negative,
                "negative_type": negative_type,
                "domain": domain

            })

        return pd.DataFrame(rows)

    # =====================================================
    # SAVE
    # =====================================================

    def save_dataset(
        self,
        output_dir,
        num_triplets
    ):

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        df = self.generate_triplet_data(
            num_triplets
        )

        output_file = (
            output_dir
            / "bi_encoder_train.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"\nGenerated {len(df)} triplets"
        )

        print(
            f"Saved to: {output_file}"
        )

        print(
            df["negative_type"]
            .value_counts()
        )

        return df


# =====================================================
# MAIN
# =====================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--skills_dir",
        default="backend/app/core/skills"
    )

    parser.add_argument(
        "--templates_dir",
        default="training/templates"
    )

    parser.add_argument(
        "--output_dir",
        default="data/training"
    )

    parser.add_argument(
        "--num_triplets",
        type=int,
        default=10000
    )

    args = parser.parse_args()

    generator = SyntheticDataGeneratorV2(
        args.skills_dir,
        args.templates_dir
    )

    generator.save_dataset(
        args.output_dir,
        args.num_triplets
    )


if __name__ == "__main__":
    main()
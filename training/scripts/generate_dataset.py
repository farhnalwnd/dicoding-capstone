import json
import random
import os
import argparse
import pandas as pd
from pathlib import Path

class SyntheticDataGenerator:
    def __init__(self, skills_dir, templates_dir):
        self.skills_dir = Path(skills_dir)
        self.templates_dir = Path(templates_dir)
        self.domains_config = self._load_domain_configs()
        self.templates = self._load_templates()
        self.slot_data = self._prepare_slot_data()
    
    def _load_domain_configs(self):
        """Load all domain JSON files from the skills folder"""
        configs = {}
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found at: {self.skills_dir}")
        for f in self.skills_dir.glob("*.json"):
            with open(f, "r") as file:
                configs[f.stem] = json.load(file)
        return configs
    
    def _load_templates(self):
        """Load template JSON files (anchor, positive, negative)"""
        templates = {}
        for name in ["anchor_templates", "positive_templates", "negative_templates"]:
            f = self.templates_dir / f"{name}.json"
            if not f.exists():
                raise FileNotFoundError(f"Template file not found at: {f}")
            with open(f, "r") as file:
                templates[name] = json.load(file)
        return templates
    
    def _prepare_slot_data(self):
        """Prepare support lists for slot filling"""
        return {
            "company": ["Google", "Microsoft", "Gojek", "Tokopedia", "Shopee", "Traveloka", "Bukalapak", "Bank Mandiri", "BCA", "Pertamina", "Unilever"],
            "role": ["Specialist", "Staff", "Manager", "Lead", "Officer", "Coordinator", "Analyst", "Engineer", "Developer"],
            "years": ["1", "2", "3", "4", "5", "6", "7", "8", "10"],
            "team": ["Operations", "Product", "Data", "Engineering", "Marketing", "Business", "Management", "Finance", "Legal"],
            "project_count": ["3", "5", "10", "lebih dari 5", "berbagai"],
            "provider": ["Google Cloud", "AWS", "Microsoft", "Coursera", "Udemy", "BNSP", "Project Management Institute"]
        }
    
    def _fill_template(self, template, domain, is_positive=True):
        """Fill a template string with random slot values"""
        config = self.domains_config.get(domain, self.domains_config.get("general"))
        skills = config.get("skills", ["Microsoft Office", "Communication"])
        projects = config.get("projects", ["office operations"])
        unrelated_industries = config.get("unrelated_industries", ["Agriculture", "Manufacturing"])
        unrelated_roles = config.get("unrelated_roles", ["Technician", "Operator"])
        unrelated_tools = config.get("unrelated_tools", ["Forklift", "Welding Machine"])
        
        # Replace {skill} placeholders
        if "{skill}" in template:
            template = template.replace("{skill}", random.choice(skills))
        if "{skill1}" in template or "{skill2}" in template:
            if len(skills) >= 2:
                sampled_skills = random.sample(skills, 2)
            else:
                sampled_skills = [skills[0], skills[0]]
            if "{skill1}" in template:
                template = template.replace("{skill1}", sampled_skills[0])
            if "{skill2}" in template:
                template = template.replace("{skill2}", sampled_skills[1])
        if "{skill3}" in template:
            template = template.replace("{skill3}", random.choice(skills))
            
        # Replace dynamic domain-specific placeholders
        if "{project}" in template:
            template = template.replace("{project}", random.choice(projects))
        if "{industry_unrelated}" in template:
            template = template.replace("{industry_unrelated}", random.choice(unrelated_industries))
        if "{role_unrelated}" in template:
            template = template.replace("{role_unrelated}", random.choice(unrelated_roles))
        if "{tool_unrelated}" in template:
            template = template.replace("{tool_unrelated}", random.choice(unrelated_tools))
        
        # Replace other standard slots
        for slot, values in self.slot_data.items():
            slot_placeholder = "{" + slot + "}"
            if slot_placeholder in template:
                template = template.replace(slot_placeholder, random.choice(values))
        
        # For negative samples, handle unrelated slots
        if not is_positive and "{skill_unrelated}" in template:
            # Pick a skill from a completely different domain
            other_domains = [d for d in self.domains_config.keys() if d != domain]
            if other_domains:
                other_domain = random.choice(other_domains)
                other_skills = self.domains_config[other_domain].get("skills", ["Communication"])
                template = template.replace("{skill_unrelated}", random.choice(other_skills))
            else:
                template = template.replace("{skill_unrelated}", "Graphic Design")
        
        return template
    
    def generate_triplet_data(self, num_examples=2000):
        """Generate triplet data (anchor, positive, negative) for Bi-Encoder"""
        data = []
        domains = list(self.domains_config.keys())
        
        anchor_templates = self.templates.get("anchor_templates", {})
        positive_templates = self.templates.get("positive_templates", {})
        negative_templates = self.templates.get("negative_templates", {})
        
        for _ in range(num_examples):
            # Pick domain for anchor & positive
            domain = random.choice(domains)
            
            # Fetch templates (all from same domain)
            anchor_tmpls = anchor_templates.get(domain, anchor_templates.get("general", []))
            positive_tmpls = positive_templates.get(domain, positive_templates.get("general", []))
            negative_tmpls = negative_templates.get(domain, negative_templates.get("general", []))
            
            if not anchor_tmpls or not positive_tmpls or not negative_tmpls:
                continue
            
            anchor = self._fill_template(random.choice(anchor_tmpls), domain)
            positive = self._fill_template(random.choice(positive_tmpls), domain, is_positive=True)
            negative = self._fill_template(random.choice(negative_tmpls), domain, is_positive=False)
            
            data.append({
                "anchor": anchor,
                "positive": positive,
                "negative": negative
            })
            
        return pd.DataFrame(data)
    
    def save_dataset(self, output_dir, num_triplets=2000):
        """Generate and save the triplet dataset to CSV file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        df_triplet = self.generate_triplet_data(num_triplets)
        df_triplet.to_csv(output_path / "bi_encoder_train.csv", index=False)
        print(f"Generated and saved Bi-Encoder triplet dataset to: {output_path / 'bi_encoder_train.csv'}")
        
        return df_triplet

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data for Bi-Encoder training.")
    parser.add_argument("--skills_dir", type=str, default="backend/app/core/skills", help="Path to skills configs.")
    parser.add_argument("--templates_dir", type=str, default="training/templates", help="Path to templates JSON.")
    parser.add_argument("--output_dir", type=str, default="data/training", help="Output directory for generated datasets.")
    parser.add_argument("--num_triplets", type=int, default=2000, help="Number of triplet examples.")
    
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(
        skills_dir=args.skills_dir,
        templates_dir=args.templates_dir
    )
    
    generator.save_dataset(
        output_dir=args.output_dir,
        num_triplets=args.num_triplets
    )

if __name__ == "__main__":
    main()

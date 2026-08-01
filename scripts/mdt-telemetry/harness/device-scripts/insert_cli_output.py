#!/usr/bin/env python3
"""Insert CLI output from cli-outputs.json into cli-reference.md.
Adds a '### CLI Output' subsection after '### CLI Show Commands' for each section.
"""

import json
import re


def insert_cli_output(md_path, outputs_path, out_path):
    with open(outputs_path) as f:
        cli_data = json.load(f)

    with open(md_path) as f:
        lines = f.readlines()

    result = []
    current_section = None
    inserted_for_section = set()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Track current section
        heading = re.match(r"^## (\d+)\.\s+", line)
        if heading:
            current_section = heading.group(1)

        # Find the RESTCONF GET heading — insert CLI Output before it
        if (current_section and
            current_section not in inserted_for_section and
            line.strip() == "### RESTCONF GET"):

            section_data = cli_data.get(current_section, {})
            if section_data:
                # Insert CLI Output section before RESTCONF GET
                result.append("### CLI Output\n")
                result.append("\n")

                for cmd, output in section_data.items():
                    result.append(f"**`{cmd}`**\n")
                    result.append("\n")
                    if output.strip():
                        result.append("```\n")
                        result.append(output + "\n")
                        result.append("```\n")
                    else:
                        result.append("> Feature not active — no output returned.\n")
                    result.append("\n")

                result.append("---\n")
                result.append("\n")
                inserted_for_section.add(current_section)

        result.append(line)
        i += 1

    with open(out_path, "w") as f:
        f.writelines(result)

    print(f"Inserted CLI output for {len(inserted_for_section)} sections")
    print(f"Written to {out_path}")


if __name__ == "__main__":
    insert_cli_output("cli-reference.md", "cli-outputs.json", "cli-reference.md")

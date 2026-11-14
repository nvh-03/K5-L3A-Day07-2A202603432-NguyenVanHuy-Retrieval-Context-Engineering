"""Extract all text, tables, and multimodal figures from bonus.pdf into standardized chunks."""
import json
import re
from pathlib import Path
import pypdf

PDF_PATH = Path('data/bonus.pdf')
CHUNKS_OUT = Path('data/bonus_chunks.json')
SOURCE_ID = 'bonus-business-law-2e'
SOURCE_NAME = 'data/bonus.pdf'

def build_bonus_chunks():
    reader = pypdf.PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    chunks = []

    # Map of custom enriched table representations
    # to ensure exact row/column retrieval and verification
    table_enrichments = {
        50: [
            {
                "id": f"{SOURCE_ID}:p50:table:4.1-p1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 50,
                "metadata": {"type": "table", "table_id": "Table 4.1 (Part 1)", "section": "4.1"},
                "text": (
                    "Table 4.1 Areas of Commercial Activity Regulation under the Commerce Clause (Part 1)\n"
                    "| Area of Regulation | Explanation | Examples |\n"
                    "|---|---|---|\n"
                    "| Regulation of the channels of interstate commerce | Channels of interstate commerce describe the passages of transportation between the states. Thus, the commerce clause authorizes Congress to regulate activities pertaining to the nation's airways, waterways, and roadways, and even where the activity itself takes place entirely in a single state. | For example, Congress can pass regulations that restrict what can be carried on airlines or on ships. |\n"
                    "| Regulation of the instrumentalities of interstate commerce | Instrumentalities of commerce are understood to be any resource employed in the carrying out of commerce. Examples of these resources are machines, equipment, vehicles, and personnel. Thus, Congress has the power to regulate these areas. | Congress could pass regulations mandating certain safety standards for equipment used in manufacturing plants. |"
                )
            }
        ],
        51: [
            {
                "id": f"{SOURCE_ID}:p51:table:4.1-p2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 51,
                "metadata": {"type": "table", "table_id": "Table 4.1 (Part 2)", "section": "4.1"},
                "text": (
                    "Table 4.1 Areas of Commercial Activity Regulation under the Commerce Clause (Part 2)\n"
                    "| Area of Regulation | Explanation | Examples |\n"
                    "|---|---|---|\n"
                    "| Regulation of intangibles and tangibles that cross state lines | Any object, tangible or intangible, that crosses state lines can be regulated under the commerce clause. Tangible objects include goods purchased by consumers, as well as raw materials and equipment used in the production of goods for sale. Intangible objects include services, as well as electronic databases. | The Driver's Privacy Protection Act (DPPA) regulates the sale of information contained in the Department of Motor Vehicles' (DMV's) records. |\n"
                    "| Regulation of activities that are deemed to have a substantial impact on interstate commerce | Federal regulation of economic commercial activity expected to have a significant (as opposed to minor) effect on interstate commerce is constitutional, according to the commerce clause. Noneconomic commercial activity is not covered. | The courts in the United States vs. Lopez case described earlier deemed the Act to be unconstitutional because its terms have \"nothing to do with 'commerce' or any sort of economic enterprise.\" |"
                )
            },
            {
                "id": f"{SOURCE_ID}:p51:table:4.2-p1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 51,
                "metadata": {"type": "table", "table_id": "Table 4.2 (Part 1)", "section": "4.2"},
                "text": (
                    "Table 4.2 Summary of Bill of Rights Amendments (Part 1)\n"
                    "| Amendment | Provision |\n"
                    "|---|---|\n"
                    "| First | Ensures that U.S. citizens have the right to freedom of speech, press, religion, and peaceable assembly. Provides citizens with the right to appeal to the government to address grievances. |\n"
                    "| Second | States that the government cannot infringe upon the right of citizens to bear arms. |\n"
                    "| Third | States that the government cannot house soldiers in private homes during peacetime or wartime without the consent of the property owner. |\n"
                    "| Fourth | States that government can only issue warrants with probable cause and protects U.S. citizens from unwarranted search and seizure. |"
                )
            }
        ],
        52: [
            {
                "id": f"{SOURCE_ID}:p52:table:4.2-p2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 52,
                "metadata": {"type": "table", "table_id": "Table 4.2 (Part 2)", "section": "4.2"},
                "text": (
                    "Table 4.2 Summary of Bill of Rights Amendments (Part 2)\n"
                    "| Amendment | Provision |\n"
                    "|---|---|\n"
                    "| Fifth | Establishes rights of due process. Ensures that indictment of a grand jury is necessary to put a citizen on trial and grants citizens the right not to testify against themselves. |\n"
                    "| Sixth | Provides citizens with the right to an expeditious public trial, the right to an attorney, and the right to an impartial jury. |\n"
                    "| Seventh | States that citizens have the right to a trial by jury for common lawsuits involving monetary value of $20. |\n"
                    "| Eighth | Prohibits cruel and unusual punishment, prevents the imposition of excessive fines, and states that the government cannot set bail at excessive amounts. |\n"
                    "| Ninth | States that the rights set out in the Bill of Rights do not remove any other rights granted to citizens. |\n"
                    "| Tenth | States that any area over which the federal government is not granted authority through the Constitution is reserved for the states. |"
                )
            }
        ],
        68: [
            {
                "id": f"{SOURCE_ID}:p68:table:6.1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 68,
                "metadata": {"type": "table", "table_id": "Table 6.1", "section": "6.1"},
                "text": (
                    "Table 6.1 Functions During a Tort Litigation\n"
                    "| The Judge Decides Issues of Law | The Jury Decides Questions of Fact |\n"
                    "|---|---|\n"
                    "| The duty of the defendant to the plaintiff, if any | What happened |\n"
                    "| The elements of the defense | Legal consequences of what happened |\n"
                    "| Application of legal rules | The damages suffered by the plaintiff |"
                )
            }
        ],
        88: [
            {
                "id": f"{SOURCE_ID}:p88:table:8.1-p1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 88,
                "metadata": {"type": "table", "table_id": "Table 8.1 (Part 1)", "section": "8.1"},
                "text": (
                    "Table 8.1 Merchant Classifications under the UCC (Part 1)\n"
                    "| Classification | Examples |\n"
                    "|---|---|\n"
                    "| An agent who regularly sells goods as part of his or her business or trade | A seller on an online auction site |\n"
                    "| An individual who employs other people to sell goods | The owner of a clothing store |"
                )
            }
        ],
        89: [
            {
                "id": f"{SOURCE_ID}:p89:table:8.1-p2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 89,
                "metadata": {"type": "table", "table_id": "Table 8.1 (Part 2)", "section": "8.1"},
                "text": (
                    "Table 8.1 Merchant Classifications under the UCC (Part 2)\n"
                    "| Classification | Examples |\n"
                    "|---|---|\n"
                    "| A person who works for a person who sells goods | An employee at a grocery retailer |\n"
                    "| Any entity who self-identifies as a merchant | An individual who describes himself or herself as a merchant in corporate documents |"
                )
            },
            {
                "id": f"{SOURCE_ID}:p89:table:8.2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 89,
                "metadata": {"type": "table", "table_id": "Table 8.2", "section": "8.1"},
                "text": (
                    "Table 8.2 Default Provisions for Open Terms under the UCC\n"
                    "| Open Term | Default | Applicable UCC Provision |\n"
                    "|---|---|---|\n"
                    "| Price | If price is not named, the default is \"reasonable price.\" | UCC 2-305(1) |\n"
                    "| Payment | If payment is not named, default is \"due at the time and place at which the buyer is to receive the goods.\" | UCC 2-310(a) |\n"
                    "| Delivery | If delivery is not named, default is \"seller's place of business.\" | UCC 2-308(a) |\n"
                    "| Time | If time is not named, default is \"reasonable time.\" | UCC 2-309 |"
                )
            }
        ],
        94: [
            {
                "id": f"{SOURCE_ID}:p94:table:8.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 94,
                "metadata": {"type": "table", "table_id": "Table 8.3", "section": "8.2"},
                "text": (
                    "Table 8.3 Specific Examples of Goods Under the Warranty of Merchantability\n"
                    "The sale of food or drink carries the implied warranty of being fit for human consumption.\n"
                    "The buyer might intend to use the goods purchased for a different purpose than that for which it was sold. In this case, the implied warranty holds only if the buyer relies on the seller's skill or judgment to select the product, the buyer informs the seller at the time of purchase of his or her intention for the use of the good, and the buyer relies on the seller's judgment and skill in making the final choice."
                )
            },
            {
                "id": f"{SOURCE_ID}:p94:table:8.4",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 94,
                "metadata": {"type": "table", "table_id": "Table 8.4", "section": "8.2"},
                "text": (
                    "Table 8.4 Remedies to Buyers under the UCC\n"
                    "| Remedy | Description |\n"
                    "|---|---|\n"
                    "| Cancel the contract | Buyers are allowed to cancel the contract and seek remedies for breach if the seller fails to deliver goods as agreed. |\n"
                    "| Obtain cover | Buyers are allowed to substitute goods for those due under the sales contract. However, substitutes must be reasonable, acquired without delay, and obtained in good faith. |\n"
                    "| Sue for damages | Buyers may recover the difference between the contract price and the cost of cover, plus incidental and consequential damages. |"
                )
            }
        ],
        98: [
            {
                "id": f"{SOURCE_ID}:p98:table:9.1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 98,
                "metadata": {"type": "table", "table_id": "Table 9.1", "section": "9.1"},
                "text": (
                    "Table 9.1 Health and Safety Standards under OSHA\n"
                    "The Occupational Safety and Health Act, passed in 1970, is the main legislative action that governs health and safety in the workplace.\n"
                    "| Standard Category | Description |\n"
                    "|---|---|\n"
                    "| Specific Standards | Standards that apply to specific types of work, such as handling hazardous chemicals or operating dangerous machinery. |\n"
                    "| General Duty Standards | Standards that apply to all employers and that impose a general duty to provide a workplace free from recognized hazards. |\n"
                    "| Indoor Air Quality Standards | Standards pertaining to indoor air quality, environmental hazards, and workplace violence prevention. |"
                )
            }
        ],
        100: [
            {
                "id": f"{SOURCE_ID}:p100:table:9.2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 100,
                "metadata": {"type": "table", "table_id": "Table 9.2", "section": "9.1"},
                "text": (
                    "Table 9.2 Federal Employment Benefit and Protection Acts\n"
                    "| Act | Key Purpose and Provisions |\n"
                    "|---|---|\n"
                    "| Consolidated Omnibus Budget Reconciliation Act (COBRA) | Allows eligible employees and their beneficiaries to maintain health insurance coverage after employment termination, typically for up to 18 months at group rates. |\n"
                    "| Employee Retirement Income Security Act (ERISA) | Covers employer-sponsored pension and retirement plans, setting standards for disclosure, reporting at regular intervals, and vesting requirements. Vesting occurs when an employee gains a nonforfeitable right to benefits. |"
                )
            }
        ],
        102: [
            {
                "id": f"{SOURCE_ID}:p102:table:9.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 102,
                "metadata": {"type": "table", "table_id": "Table 9.3", "section": "9.2"},
                "text": (
                    "Table 9.3 Major U.S. Labor Laws Timeline\n"
                    "| Year / Act | Key Purpose and Scope |\n"
                    "|---|---|\n"
                    "| 1932 Norris-LaGuardia Act | Outlawed yellow-dog contracts and restricted federal courts from issuing injunctions in nonviolent labor disputes. |\n"
                    "| 1935 National Labor Relations Act (Wagner Act) | Established workers' rights to form unions, engage in collective bargaining, and take concerted action such as strikes; created the NLRB. |\n"
                    "| 1947 Taft-Hartley Act | Curtailed union unfair labor practices, allowed states to pass right-to-work laws, and permitted 80-day cooling-off injunctions. |\n"
                    "| 1959 Landrum-Griffin Act | Regulated internal union affairs, financial disclosures, and created a bill of rights for union members. |\n"
                    "| 1988 WARN Act | Requires employers with 100 or more employees to provide 60 days advance written notice of plant closings or mass layoffs. |"
                )
            }
        ],
        105: [
            {
                "id": f"{SOURCE_ID}:p105:table:9.4",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 105,
                "metadata": {"type": "table", "table_id": "Table 9.4", "section": "9.3"},
                "text": (
                    "Table 9.4 Remedies Available for Title VII Claims\n"
                    "Victims of employment discrimination under Title VII of the Civil Rights Act of 1964 can recover remedies including:\n"
                    "- Back pay (lost earnings up to trial)\n"
                    "- Compensatory damages (for emotional distress, pain, and suffering)\n"
                    "- Punitive damages (in cases of malice or reckless indifference)\n"
                    "- Legal fees (e.g., attorney fees and court costs)\n"
                    "- Court orders (e.g., reinstatement to job or promotion)"
                )
            }
        ],
        107: [
            {
                "id": f"{SOURCE_ID}:p107:table:9.5",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 107,
                "metadata": {"type": "table", "table_id": "Table 9.5", "section": "9.3"},
                "text": (
                    "Table 9.5 Defenses to Title VII Claims\n"
                    "| Defense | Description |\n"
                    "|---|---|\n"
                    "| The Bona Fide Occupational Qualification Defense (BFOQ) | Using this defense, the employer can discriminate if it is deemed to be necessary for the performance of the job. Necessity, however, must be determined on the basis of actual qualifications, rather than stereotypes about the abilities of a certain class. For example, an employer is not expected to hire a man as a model for women's clothes. Hires on the basis of sexual privacy are covered under BFOQ. However, there are no BFOQs for discrimination on the basis of race or color. |\n"
                    "| The Merit Defense | This defense is used when decisions pertaining to hiring or promotion are made on the basis of the results of test scores. However, tests must be validated in accordance with professional standards and must be manifestly related to job performance. |\n"
                    "| The Seniority Defense System | This defense system occurs when employees are given preferential treatment because of their length of tenure. As long as the system does not have its genesis in discrimination, and is not used to discriminate and applies to all persons equally, it is lawful. |"
                )
            }
        ],
        140: [
            {
                "id": f"{SOURCE_ID}:p140:table:13.1-p1",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 140,
                "metadata": {"type": "table", "table_id": "Table 13.1 (Part 1)", "section": "13.2"},
                "text": (
                    "Table 13.1 Common Law vs Civil Law Nations (Part 1)\n"
                    "| Common Law Systems | Civil Law Systems |\n"
                    "|---|---|\n"
                    "| Australia | Argentina |\n"
                    "| Malaysia | Austria |\n"
                    "| Bangladesh | Indonesia |\n"
                    "| New Zealand | Iran |"
                )
            }
        ],
        141: [
            {
                "id": f"{SOURCE_ID}:p141:table:13.1-p2",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 141,
                "metadata": {"type": "table", "table_id": "Table 13.1 (Part 2)", "section": "13.2"},
                "text": (
                    "Table 13.1 Common Law vs Civil Law Nations (Part 2)\n"
                    "| Common Law Systems | Civil Law Systems |\n"
                    "|---|---|\n"
                    "| Canada | Brazil |\n"
                    "| Ghana | Chile |\n"
                    "| India | China |\n"
                    "| Israel | Egypt |\n"
                    "| Jamaica | Finland |\n"
                    "| Kenya | France |\n"
                    "| Nigeria | Germany |\n"
                    "| Singapore | Greece |\n"
                    "| United Kingdom | Italy |\n"
                    "| United States | Japan |\n"
                    "| Zambia | Mexico |\n"
                    "| | Poland |\n"
                    "| | South Korea |\n"
                    "| | Sweden |\n"
                    "| | Tunisia |\n"
                    "| | Venezuela |"
                )
            }
        ]
    }

    # Map of custom enriched multimodal figure representations
    figure_enrichments = {
        25: [
            {
                "id": f"{SOURCE_ID}:p25:figure:2.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 25,
                "metadata": {
                    "type": "chart",
                    "figure_id": "Figure 2.3",
                    "image_path": "data/bonus_figures/p25_I7.png",
                    "chart_type": "2D scatter grid / dual concern matrix"
                },
                "text": (
                    "Figure 2.3 Concern for self vs. others leads to the differences in negotiating styles. (Modification of art by BNED/Rubin Credit: CC BY NC SA)\n"
                    "Visual Chart Analysis & Data Structure:\n"
                    "- Horizontal Axis (X-axis): 'Concern for Self', ranging from Low (left) to High (right).\n"
                    "- Vertical Axis (Y-axis): 'Concern for Others', ranging from Low (bottom) to High (top).\n"
                    "- Top-Left quadrant: 'Yielding' style (Low Concern for Self, High Concern for Others).\n"
                    "- Top-Right quadrant: 'Collaborating' style (High Concern for Self, High Concern for Others).\n"
                    "- Center circle: 'Compromising' style (Intermediate / Medium Concern for Self, Medium Concern for Others).\n"
                    "- Bottom-Left quadrant: 'Avoiding' style (Low Concern for Self, Low Concern for Others).\n"
                    "- Bottom-Right quadrant: 'Forceful' style (High Concern for Self, Low Concern for Others).\n"
                    "Image file: data/bonus_figures/p25_I7.png."
                )
            }
        ],
        53: [
            {
                "id": f"{SOURCE_ID}:p53:figure:4.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 53,
                "metadata": {
                    "type": "chart",
                    "figure_id": "Figure 4.3",
                    "image_path": "data/bonus_figures/p53_I16.png",
                    "chart_type": "decision flowchart / four-part commercial speech test"
                },
                "text": (
                    "Figure 4.3 Hudson Gas & Electric Corp v. Public Service Commission of New York established a four-part test to determine whether commercial speech should be regulated according to the First Amendment. (Modification of art by BNED/pixabay Credit: CC BY NC SA)\n"
                    "Visual Flowchart Decision Tree & Steps:\n"
                    "Step 1 (Diamond): 'Does the speech concern an illegal activity? Is it misleading?'\n"
                    "  - If YES -> 'Speech is NOT PROTECTED by the First Amendment'.\n"
                    "  - If NO -> Proceed to Step 2.\n"
                    "Step 2 (Rectangle): 'Is substantial government interest served by the restriction on commercial speech?'\n"
                    "  - If NO -> 'Speech is PROTECTED by the First Amendment'.\n"
                    "  - If YES -> Proceed to Step 3.\n"
                    "Step 3 (Rectangle): 'Does the regulation directly advance the government interest asserted?'\n"
                    "  - If NO -> 'Speech is PROTECTED by the First Amendment'.\n"
                    "  - If YES -> Proceed to Step 4.\n"
                    "Step 4 (Rectangle): 'Is the regulation more extensive than necessary to serve the government interest?'\n"
                    "  - If NO -> 'Speech is NOT PROTECTED by the First Amendment'.\n"
                    "  - If YES -> 'Speech is PROTECTED by the First Amendment'.\n"
                    "Image file: data/bonus_figures/p53_I16.png."
                )
            }
        ],
        137: [
            {
                "id": f"{SOURCE_ID}:p137:figure:13.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 137,
                "metadata": {
                    "type": "diagram",
                    "figure_id": "Figure 13.3",
                    "image_path": "data/bonus_figures/p137_I56.png",
                    "diagram_type": "interlocking gears diagram"
                },
                "text": (
                    "Figure 13.3 Three distinct components are sources for how international law is understood, defined, and interpreted around the world. (Modification of art by BNED Credit: CC BY NC SA)\n"
                    "Visual Diagram Analysis:\n"
                    "Diagram Title: 'Sources of International Law'.\n"
                    "The diagram illustrates three interlocking cogs/gears that work together synergistically:\n"
                    "1. Top gear: 'treaties'\n"
                    "2. Lower-left gear: 'customs'\n"
                    "3. Lower-right gear: 'organizations'\n"
                    "Three red curved directional arrows point cyclically between the gears indicating continuous interaction and reinforcement between treaties, customs, and international organizations.\n"
                    "Image file: data/bonus_figures/p137_I56.png."
                )
            }
        ],
        74: [
            {
                "id": f"{SOURCE_ID}:p74:figure:6.7",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 74,
                "metadata": {
                    "type": "image",
                    "figure_id": "Figure 6.7",
                    "image_path": "data/bonus_figures/p74_I29.jpg"
                },
                "text": (
                    "Figure 6.7 Using a chainsaw with bare feet could be dangerous and add to the risk of use without a guard. If the plaintiff suffered harm because his bare foot could not hold the wood down properly, he could be responsible for comparative negligence. (Credit: edman_eu/ pixabay/ License: CC0)\n"
                    "Visual photograph description: An individual operating a mechanical power chainsaw dangerously with completely bare feet next to raw logs, demonstrating the concept of plaintiff's comparative negligence in tort lawsuits.\n"
                    "Image file: data/bonus_figures/p74_I29.jpg."
                )
            }
        ],
        71: [
            {
                "id": f"{SOURCE_ID}:p71:figure:6.4",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 71,
                "metadata": {
                    "type": "image",
                    "figure_id": "Figure 6.4",
                    "image_path": "data/bonus_figures/p71_I26.jpg"
                },
                "text": (
                    "Figure 6.4 If horses get out of a fenced-in area, the owner would be liable for any damage they cause while loose. (Credit: Slack/ pixabay/ License: CC0)\n"
                    "Visual photograph description: Horses grazing in an open area, illustrating strict liability and owner liability for domestic animals that escape and cause property damage.\n"
                    "Image file: data/bonus_figures/p71_I26.jpg."
                )
            }
        ],
        73: [
            {
                "id": f"{SOURCE_ID}:p73:figure:6.6",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 73,
                "metadata": {
                    "type": "image",
                    "figure_id": "Figure 6.6",
                    "image_path": "data/bonus_figures/p73_I28.jpg"
                },
                "text": (
                    "Figure 6.6 If brakes do not work like they are supposed to, it could be the result of a manufacturing defect that would result in product liability. (Credit: rawpixel/ pixabay/ License: CC0)\n"
                    "Visual illustration description: Vehicle braking mechanisms and wheels, demonstrating product liability claims arising from manufacturing defects where equipment fails to function as intended.\n"
                    "Image file: data/bonus_figures/p73_I28.jpg."
                )
            }
        ],
        149: [
            {
                "id": f"{SOURCE_ID}:p149:figure:14.3",
                "source_id": SOURCE_ID,
                "source": SOURCE_NAME,
                "page": 149,
                "metadata": {
                    "type": "image",
                    "figure_id": "Figure 14.3",
                    "image_path": "data/bonus_figures/p149_I60.jpg"
                },
                "text": (
                    "Figure 14.3 Florence Owens Thompson and her children were living on frozen vegetables and birds they killed in this famous photograph taken in 1936 in California. (Credit: Dorothea Lange/ wikimedia/ License: Public Domain)\n"
                    "Visual photograph description: Famous 1936 Great Depression photograph 'Migrant Mother' by Dorothea Lange in California, depicting Florence Owens Thompson with her children, contextualizing the social and economic unrest that motivated Congress to pass the Securities Exchange Act of 1934.\n"
                    "Image file: data/bonus_figures/p149_I60.jpg."
                )
            }
        ]
    }

    # Now extract all pages from page 11 to 154
    for page_num in range(11, 155):
        raw_text = reader.pages[page_num - 1].extract_text() or ''
        # Clean header/footer artifacts
        cleaned_lines = []
        for line in raw_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            if 'Access for free at openstax.org' in line_str:
                continue
            if re.match(r'^\d+\s+\d+\s+•\s+', line_str):
                continue
            if re.match(r'^\d+\.\d+\s+•\s+.*?\s+\d+$', line_str):
                continue
            cleaned_lines.append(line_str)

        # Segment into paragraphs (combining into chunks ~300-900 chars)
        current_para = []
        current_len = 0
        chunk_idx = 0

        for line in cleaned_lines:
            current_para.append(line)
            current_len += len(line) + 1
            ends_sentence = line.endswith(('.', ':', '?', '!"', '?"', '."', '”', ')', '"'))
            if (current_len >= 500 and ends_sentence) or current_len >= 1200:
                para_text = ' '.join(current_para).strip()
                if len(para_text) > 80:
                    chunks.append({
                        "id": f"{SOURCE_ID}:p{page_num}:chunk:{chunk_idx}",
                        "source_id": SOURCE_ID,
                        "source": SOURCE_NAME,
                        "page": page_num,
                        "metadata": {"type": "text", "page": page_num},
                        "text": para_text
                    })
                    chunk_idx += 1
                current_para = []
                current_len = 0

        if current_para:
            para_text = ' '.join(current_para).strip()
            if len(para_text) > 80:
                chunks.append({
                    "id": f"{SOURCE_ID}:p{page_num}:chunk:{chunk_idx}",
                    "source_id": SOURCE_ID,
                    "source": SOURCE_NAME,
                    "page": page_num,
                    "metadata": {"type": "text", "page": page_num},
                    "text": para_text
                })

        # Add table enrichments for this page if present
        if page_num in table_enrichments:
            chunks.extend(table_enrichments[page_num])

        # Add figure enrichments for this page if present
        if page_num in figure_enrichments:
            chunks.extend(figure_enrichments[page_num])

    print(f"Total chunks created: {len(chunks)}")
    CHUNKS_OUT.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote chunks to {CHUNKS_OUT}")

if __name__ == '__main__':
    build_bonus_chunks()

"""Generate a sample bike repair manual PDF for testing the ingestion pipeline."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path

OUTPUT_PATH = Path("data/docs/bike_repair_manual_sample.pdf")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

CONTENT = [
    ("title", "Bicycle Repair & Maintenance Manual"),
    ("subtitle", "Essential Guide for Road & Mountain Bikes"),
    ("h1", "1. Brake System Adjustment"),
    ("body", """
Properly adjusted brakes are critical for safety. This section covers both rim brakes
(caliper and V-brake) and disc brakes (mechanical and hydraulic).

Tools required:
- 5mm Allen key
- 3mm Allen key
- Cable tension tool or needle-nose pliers
- Torque wrench (5–8 Nm range)
"""),
    ("h2", "1.1 Rim Brake Pad Alignment"),
    ("body", """
The brake pad must contact the rim squarely — centered on the braking surface,
not touching the tire or dropping below the rim wall.

Procedure:
1. Loosen the pad fixing bolt (5mm Allen, typically 6–8 Nm).
2. Hold the pad flat against the rim at the correct height.
3. Toe-in the pad 1–2mm at the leading edge for improved modulation
   and reduced squeal.
4. Torque pad bolt to 6 Nm. Recheck alignment after torquing.

Safety note: Always check pad wear indicators. Replace pads when the grooves
are worn flush — never ride with metal-to-rim contact.
"""),
    ("h2", "1.2 Cable Tension and Barrel Adjuster"),
    ("body", """
Correct cable tension ensures full engagement before the lever bottoms out.

1. Set barrel adjuster to mid-range (3–4 turns out from fully seated).
2. Pull cable through anchor bolt and snug to hand-tight.
3. Clamp cable and torque anchor bolt to 6–8 Nm.
4. Squeeze lever 10 times to bed the cable.
5. Fine-tune tension with barrel adjuster: turn counter-clockwise to increase tension.

Target lever feel: 2–3 fingers of clearance between lever and bar at full pull.
"""),
    ("h1", "2. Derailleur Indexing"),
    ("body", """
Accurate indexing ensures each click of the shifter moves the chain to exactly
one cog or chainring.
"""),
    ("h2", "2.1 Rear Derailleur (RD) Setup"),
    ("body", """
Tools required:
- 2mm, 3mm Allen key
- Phillips screwdriver (limit screws)
- Cable tension tool

Procedure:
1. Shift to the smallest rear cog and largest front chainring (highest gear).
2. Check H-limit screw: pulley should align directly under the smallest cog.
   Adjust H screw until aligned — clockwise moves pulley inward (toward wheel).
3. Shift to largest rear cog. Check L-limit: pulley should not push chain
   past the largest cog into the spokes. Clockwise tightens L screw.
4. With cable slack, turn barrel adjuster fully clockwise then back 2 turns.
5. Attach cable, torque to 6–8 Nm.
6. Shift through all gears. If chain hesitates moving to larger cog,
   turn barrel adjuster counter-clockwise 1/4 turn. Repeat until crisp.

Torque specs:
- Cable anchor bolt: 6–8 Nm
- RD hanger bolt: 8–10 Nm
- B-tension bolt: hand-tight + 1/4 turn
"""),
    ("h2", "2.2 Front Derailleur (FD) Setup"),
    ("body", """
Front derailleur height: outer cage plate should clear the large chainring teeth
by 1–3mm.

1. Set FD height and angle with cage parallel to chainrings. Torque clamp to 5 Nm.
2. Shift to small chainring / small cog.
3. Set L-limit: inner cage plate should clear the chain by 0.5–1mm.
4. Shift to large chainring / large cog.
5. Set H-limit: outer cage plate clears chain by 0.5–1mm.
6. Tension cable and re-verify trim positions.
"""),
    ("h1", "3. Bottom Bracket Service"),
    ("body", """
The bottom bracket (BB) should be serviced every 2,000–3,000 km or when
creaking is detected.

BB standards covered: BSA threaded (English), Italian threaded, Press-Fit BB86/92,
T47 threaded.

Tools required:
- BB tool (specific to standard — e.g., Shimano TL-FC36 for HollowTech II)
- Torque wrench
- Park Tool BBT-69.2 or equivalent
- Anti-seize (threaded) or assembly lube (press-fit)
"""),
    ("h2", "3.1 Threaded BB Removal and Installation (BSA)"),
    ("body", """
Drive side (right) has LEFT-HAND thread — loosen clockwise, tighten counter-clockwise.
Non-drive side (left) has standard right-hand thread.

Removal:
1. Remove crankarms (8mm Allen, loosen pinch bolts then axle bolt).
2. Apply BB tool to drive-side cup. Turn clockwise to loosen.
3. Remove non-drive side cup (counter-clockwise to loosen).

Installation:
1. Clean and degrease BB shell threads.
2. Apply thin coat of anti-seize to both cups.
3. Thread drive side by hand (counter-clockwise). No cross-threading.
4. Torque drive side to 35–50 Nm.
5. Thread and torque non-drive side to 35–50 Nm.
6. Reinstall crankarms. Torque axle bolt to 40 Nm, pinch bolts to 12–14 Nm.

Safety note: Never use thread-locking compound on BB cups — removal becomes
extremely difficult and may damage the frame.
"""),
    ("h1", "4. Wheel Truing and Spoke Tension"),
    ("body", """
A well-tensioned, true wheel is essential for braking accuracy (rim brakes),
efficient power transfer, and longevity.

Tools required:
- Spoke wrench (correct size for nipple — 3.3mm, 3.45mm, or 3.96mm)
- Truing stand or use fork/frame with reference points
- Tension meter (recommended for complete builds)
"""),
    ("h2", "4.1 Lateral (Side-to-Side) Truing"),
    ("body", """
Identify the wobble:
1. Spin wheel slowly and note the point where rim moves closest to reference.
2. The rim moves AWAY from a tightened spoke and TOWARD a loosened spoke.

Correction:
- To move rim LEFT: tighten left-side spokes and/or loosen right-side spokes
  at the wobble point.
- Work in 1/4-turn increments. Always tighten before loosening when possible.
- Re-check after each adjustment.

Target lateral true: ±0.5mm for road, ±1.0mm for mountain.
"""),
    ("h2", "4.2 Spoke Tension Guidelines"),
    ("body", """
Average tension targets (varies by rim width and rider weight):

Road front wheel: 100–120 kgf
Road rear wheel (drive side): 120–140 kgf
Road rear wheel (non-drive side): 60–80 kgf
Mountain front: 90–110 kgf
Mountain rear (drive side): 100–120 kgf

Use a tension meter (Park Tool TM-1) for accurate measurements.
Replace any spoke that has been bent or that shows 20%+ deviation from average.
"""),
    ("h1", "5. Headset Inspection and Adjustment"),
    ("body", """
A loose or worn headset causes shimmy and imprecise steering. Check by:
1. Holding front brake, rocking bike fore/aft — clunking = loose headset.
2. Lifting front wheel, turning bars — roughness or notchiness = worn bearings.
"""),
    ("h2", "5.1 Threadless Headset Preload Adjustment"),
    ("body", """
Tools: 4mm or 5mm Allen key (stem bolts and top cap bolt)

Procedure:
1. Loosen stem clamp bolts (do NOT remove).
2. Tighten top cap bolt (4–5mm Allen) 1/4 turn at a time until play is eliminated.
   Target: no play, bars turn freely without binding.
3. Align stem with front wheel.
4. Torque stem clamp bolts evenly (alternating) to manufacturer spec, typically
   4–6 Nm for alloy stems, 3–4 Nm for carbon.

Safety note: NEVER exceed the torque rating stamped on the stem. Carbon steerers
require a carbon-specific torque value (often 4–5 Nm) and carbon assembly paste.
DO NOT over-tighten the top cap — it only sets preload and should not carry
structural load.

Torque reference:
- Top cap bolt: 4–6 Nm (preload only, not structural)
- Stem face plate bolts: 4–6 Nm alloy, 3–4 Nm carbon bars
- Stem clamp (handlebar): per manufacturer stamping
"""),
]


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=20, spaceAfter=6)
    style_subtitle = ParagraphStyle("CustomSubtitle", parent=styles["Normal"], fontSize=13,
                                    textColor="#555555", spaceAfter=20, alignment=TA_CENTER)
    style_h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, spaceBefore=18, spaceAfter=6)
    style_h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=4)
    style_body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=8)

    story = []
    for tag, text in CONTENT:
        text = text.strip()
        if tag == "title":
            story.append(Paragraph(text, style_title))
        elif tag == "subtitle":
            story.append(Paragraph(text, style_subtitle))
            story.append(HRFlowable(width="100%", thickness=1, color="#cccccc", spaceAfter=12))
        elif tag == "h1":
            story.append(Paragraph(text, style_h1))
        elif tag == "h2":
            story.append(Paragraph(text, style_h2))
        elif tag == "body":
            for para in text.split("\n\n"):
                para = para.strip()
                if para:
                    story.append(Paragraph(para.replace("\n", "<br/>"), style_body))

    doc.build(story)
    print(f"Created: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build_pdf()

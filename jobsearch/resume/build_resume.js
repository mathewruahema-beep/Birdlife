// Builds the remote-optimised master resume from ../profile.json.
// Usage: node build_resume.js            (writes Mathew_Hema_Remote_Master_Resume.docx and .txt)
// Requires the `docx` npm package (preinstalled in the Claude sandbox; `npm install docx` elsewhere).
const fs = require("fs");
const path = require("path");
let docx;
try { docx = require("docx"); } catch { docx = require(path.join(require("child_process").execSync("npm root -g").toString().trim(), "docx")); }
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, LevelFormat, BorderStyle, TabStopType } = docx;

const profile = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "profile.json"), "utf8"));
const c = profile.candidate;
const REMOTE_LINE = "Melbourne, Australia. Remote. AEST/AEDT with daily overlap to APAC, US Pacific mornings and UK afternoons.";
const DISTRIBUTED = "Fourteen years leading distributed teams across Australia, the USA, the UK and India.";

const FONT = "Calibri";
const body = (text, opts = {}) => new Paragraph({ spacing: { after: 80 }, ...opts, children: [new TextRun({ text, font: FONT, size: 21, ...(opts.run || {}) })] });
const bullet = (text) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 }, children: [new TextRun({ text, font: FONT, size: 21 })] });
const heading = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 80 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "0E7C7B", space: 2 } },
  children: [new TextRun({ text: text.toUpperCase(), font: FONT, size: 22, bold: true, color: "0E7C7B" })],
});
const roleLine = (title, org, period) => new Paragraph({
  spacing: { before: 120, after: 40 },
  tabStops: [{ type: TabStopType.RIGHT, position: 9600 }],
  children: [new TextRun({ text: `${title}, ${org}`, font: FONT, size: 22, bold: true }), new TextRun({ text: `\t${period}`, font: FONT, size: 20, color: "5F6E7C" })],
});
const labelled = (label, text) => new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: label + ". ", font: FONT, size: 21, bold: true }), new TextRun({ text, font: FONT, size: 21 })] });

const children = [
  new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: c.name.toUpperCase(), font: FONT, size: 40, bold: true, color: "172029" })] }),
  new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Head of IT | CIO | Technology Strategy, Security and Transformation", font: FONT, size: 24, color: "0E7C7B" })] }),
  body(`${c.email}  |  ${c.linkedin || "linkedin.com/in/your-handle"}  |  phone on request`, { run: { color: "5F6E7C", size: 20 } }),
  body(REMOTE_LINE + " " + DISTRIBUTED, { run: { bold: true } }),

  heading("Profile"),
  body(c.summary),
  body(c.pattern),

  heading("Selected results"),
  ...profile.highlights.map(bullet),

  heading("Capabilities"),
  ...Object.entries(profile.capabilities).map(([k, v]) => labelled(k, v)),

  heading("Technical environment"),
  ...Object.entries(profile.technical).map(([k, v]) => labelled(k, v)),

  heading("Experience"),
];
for (const e of profile.experience) {
  children.push(roleLine(e.title, e.org, e.period));
  for (const b of e.bullets) children.push(bullet(b));
}
children.push(roleLine("Senior Systems Engineer", "TrademarkDM", "Jan 2000 - Aug 2002"));
children.push(bullet("Managed infrastructure and database programming for a direct marketing firm serving Telstra and Ernst & Young; mentored junior engineers."));

children.push(heading("Board appointment"));
children.push(roleLine("Board Member", "Dandenong Community and Learning Centre", "Nov 2024 - Present"));
children.push(bullet("Three-year appointment. Board lead for information technology, security and compliance; guide policy, governance and assurance for an organisation delivering legal education and services to marginalised communities."));

children.push(heading("Education and professional development"));
for (const line of profile.credentials.slice(0, 7)) children.push(bullet(line));
children.push(bullet("Applied frameworks: ACSC Essential Eight to Maturity Level 3, ISO 27001, PCI DSS, PMBOK, ITIL service management, PRINCE2, Agile"));
children.push(body("Referees available on request.", { run: { color: "5F6E7C", size: 20 }, spacing: { before: 160 } }));

const doc = new Document({
  creator: c.name,
  title: `${c.name} resume`,
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{ properties: { page: { margin: { top: 900, bottom: 900, left: 1000, right: 1000 } } }, children }],
});

const out = path.join(__dirname, "Mathew_Hema_Remote_Master_Resume.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  // ATS plain-text twin: one column, no formatting, same content.
  const lines = [c.name, "Head of IT | CIO | Technology Strategy, Security and Transformation", `${c.email} | ${c.linkedin || ""}`.trim(), REMOTE_LINE + " " + DISTRIBUTED, "",
    "PROFILE", c.summary, c.pattern, "", "SELECTED RESULTS", ...profile.highlights.map((h) => "- " + h), "",
    "CAPABILITIES", ...Object.entries(profile.capabilities).map(([k, v]) => `${k}: ${v}`), "",
    "TECHNICAL ENVIRONMENT", ...Object.entries(profile.technical).map(([k, v]) => `${k}: ${v}`), "", "EXPERIENCE"];
  for (const e of profile.experience) { lines.push(`${e.title}, ${e.org} (${e.period})`); for (const b of e.bullets) lines.push("- " + b); lines.push(""); }
  lines.push("Senior Systems Engineer, TrademarkDM (Jan 2000 - Aug 2002)", "- Managed infrastructure and database programming for a direct marketing firm serving Telstra and Ernst & Young; mentored junior engineers.", "",
    "BOARD APPOINTMENT", "Board Member, Dandenong Community and Learning Centre (Nov 2024 - Present)", "- Board lead for information technology, security and compliance.", "",
    "EDUCATION AND PROFESSIONAL DEVELOPMENT", ...profile.credentials.map((l) => "- " + l));
  fs.writeFileSync(out.replace(".docx", ".txt"), lines.join("\n"));
  console.log("wrote", out, "and .txt");
});

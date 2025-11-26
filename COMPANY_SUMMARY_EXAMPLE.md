# How to Add Company Summaries

To add custom summaries for each company detail page, add a `company_summary` field to the **first position** under each company in `resume.yaml`.

## Example Structure

```yaml
work_experience:
  Arctic Wolf Networks:
  # -------------------------------------------------------------------------
  # Team Lead (Current Role)
  # -------------------------------------------------------------------------
  - company_summary: |-
      At Arctic Wolf Networks, I've progressed from a Triage Security Engineer to Team Lead, driving both technical innovation and team excellence. I've led the development of automation tools that saved over 2000 hours annually, while building and mentoring a high-performing security operations team. My focus has been on combining technical expertise in Python automation and detection engineering with people-first leadership that prioritizes team happiness, health, and productivity.
    job_title: Team Lead
    location: Remote
    start_date: '2024-02-01'
    end_date: Present
    responsibilities:
    # ... rest of position data
```

## Key Points

1. **Add `company_summary` to the first position only** - The code extracts it from `positions[0]`
2. **Use `|-` for multi-line text** - This preserves formatting in YAML
3. **Tailor each summary** - Write company-specific narratives about your experience there
4. **Falls back to basics.summary** - If no company_summary is provided, uses the generic resume summary

## Recommended Content for Company Summaries

For each company, consider mentioning:
- Your progression/growth at the company
- Key achievements specific to that organization
- Technologies or domains you worked with
- What made that experience unique
- How you added value to the organization

## Example Summaries

### Arctic Wolf Networks
```
At Arctic Wolf Networks, I've progressed from a Triage Security Engineer to Team Lead, driving both technical innovation and team excellence. I've led the development of automation tools that saved over 2000 hours annually, while building and mentoring a high-performing security operations team. My focus has been on combining technical expertise in Python automation and detection engineering with people-first leadership that prioritizes team happiness, health, and productivity.
```

### CarKey
```
As Lead Videographer at CarKey, I was responsible for creating compelling video content that showcased the company's innovative vehicle access solutions. I managed the entire video production pipeline, from concept development to final delivery, producing professional marketing materials that enhanced brand visibility and customer engagement.
```

### US Army
```
During my time as a Public Affairs Officer in the US Army, I served as the primary communications liaison, managing media relations and producing visual content that told the Army's story to both military and civilian audiences. I honed my leadership skills while managing complex projects under pressure and developed a strong foundation in strategic communication and team coordination.
```

## After Adding Summaries

Once you add company summaries and push to GitHub:
1. The build process will generate company pages with your custom summaries
2. Each company page will show the tailored narrative instead of the generic resume summary
3. The main resume page (index.html) will continue using `basics.summary`

Delete this file after reading - it's just a guide!

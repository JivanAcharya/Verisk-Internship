def create_pdf_from_dataframe(df, filename="universities.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, "Top Universities Information")
    y -= 30

    for _, row in df.iterrows():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"{row['rank']}. {row['name']}")
        y -= 20

        c.setFont("Helvetica", 12)
        text = f"Location: {row['Location']}\nWebsite: {row['uni_url']}\n\n{row['expanded_description']}\n"
        text += f"\nAcademic Excellence:\n- Citations: {row['scores_citations']}\n- Research: {row['scores_research']}\n- Teaching: {row['scores_teaching']}\n"
        text += f"\nTotal Students: {row['stats_number_students']} (Intl: {row['stats_pc_intl_students']})\nSubjects: {row['subjects_offered']}"

        for line in simpleSplit(text, "Helvetica", 12, width - 100):
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50

        y -= 20  # Space between universities

    c.save()

# Generate PDF
create_pdf_from_dataframe(df)
print("PDF created successfully!")

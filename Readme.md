Certainly! I'll format your markdown file to focus on the API endpoints and convert the information into a more readable table format. I'll also include instructions for installing PostgreSQL and pgvector. Please note, however, that the details about the bearer token being generated by Next.js will be mentioned as a general guideline since specific implementation details might vary.

---

### Nexus AI

Nexus AI hosts all AI-related operations. Key operations include:

- Uploading documents to S3 and returning URLs with additional metadata.
- Calculating plagiarism scores for documents using OpenAI embeddings.
- Managing project data in a database.
- Providing a QA bot endpoint for database interaction.

### Required Installations

Before using these APIs, ensure the following are installed:
- PostgreSQL: Database management system.
- pgvector: Extension for PostgreSQL to support vector operations.

### API Endpoints

1. **Upload Document**

   | Endpoint | Method | Description |
   |----------|--------|-------------|
   | `{{baseurl}}/api/projects/uploaddocument` | POST | Uploads a document and returns a URL along with metadata like domain, title, etc. |

   **Request:**
   ```markdown
   POST {{baseurl}}/api/projects/uploaddocument
   Content-Type: multipart/form-data; boundary=WebAppBoundary
   Authorization: Bearer {{student_token}}
   ```
   
**Request Body:** 
```
--WebAppBoundary
Content-Disposition: form-data; name="file"; filename="summary.docx"
Content-Type: text/plain

< ./summaries/summary1.docx
--WebAppBoundary--
```

   
   **Response:**
   ```json
   {
     "url": "https://nexusbucketpanimalar.s3.amazonaws.com/148-summary.docx",
     "content": {
       "categories": ["Internet of Things", "Home Automation", "Smart Homes"],
       "description": "The Home Automation System...",
       "domain": "Not provided",
       "institute": "Not provided",
       "theme": "Engineering",
       "title": "Home Automation System for Residential Environments"
     },
     "result": "File uploaded successfully to S3. Welcome student1@student.com!"
   }
   ```

2. **Add Project With All Details**

   | Endpoint | Method | Description |
   |----------|--------|-------------|
   | `{{baseurl}}/api/projects` | POST | Adds a project with detailed information into the database. |

   **Request:**
   ```markdown
   POST {{baseurl}}/api/projects
   Content-Type: application/json
   Authorization: Bearer {{student_token}}
   ```
   **Request Body:** 

```json
{
    "project_type": "student",
    "title": "Innovative Approaches in Renewable Energy",
    "description": "This project explores novel techniques in harnessing renewable energy sources. It aims to address the efficiency and scalability issues in solar and wind energy conversion.",
    "summary_file": "https://nexusbucketpanimalar.s3.amazonaws.com/148-summary.docx",
    "members": [
        "alice.smith@example.com"
    ],
    "institute": "Green Tech University",
    "prototype_demo": "",
    "prototype_sourcecode": "",
    "categories": ["Renewable Energy", "Sustainability", "Technology"],
    "theme": "Engineering",
    "domain": "Renewable Energy"
}
```


   
   **Response:**
   ```json
{
  "message": "Project added successfully",
  "result": {
    "project": {
      "categories": [
        "Renewable Energy",
        "Sustainability",
        "Technology"
      ],
      "date_created": "Tue, 19 Dec 2023 03:52:17 GMT",
      "date_updated": "Tue, 19 Dec 2023 03:52:17 GMT",
      "description": "This project explores novel techniques in harnessing renewable energy sources. It aims to address the efficiency and scalability issues in solar and wind energy conversion.",
      "domain": "Renewable Energy",
      "id": "f569091a-44d2-4a70-9033-6773831c870d",
      "institute": "Green Tech University",
      "members": [
        "alice.smith@example.com"
      ],
      "plagiarism_details": null,
      "project_type": "student",
      "prototype_demo": null,
      "prototype_sourcecode": null,
      "rating": null,
      "summary_file": "https://nexusbucketpanimalar.s3.amazonaws.com/148-summary.docx",
      "theme": "Engineering",
      "title": "Innovative Approaches in Renewable Energy",
      "uploaded_by": "student1@student.com"
    },
    "sourcecode": null,
    "sourcecode_plagarismscore": null,
    "summary": [
      "900ebcc2-936f-4bef-8365-55fff258ea91"
    ],
    "summary_plagarismscore": [
      {
        "project_id": "903c45af-7696-46b9-8239-e53724b65241",
        "similarity": 100
      },
      {
        "project_id": "4bcdf36b-70b9-402e-b394-d0cfb1c7e324",
        "similarity": 100
      }
    ]
  }
}
   ```

### Additional Notes

- The bearer token for API authentication is generated by Next.js.
- The API endpoints are designed to interact with the Nexus AI system for efficient management of AI-related projects and document handling.




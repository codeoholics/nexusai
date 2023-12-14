### Nexus AI


All Ai related Operations is hosted here.

- upload document
  - upload document to s3, return url , along with  other possible combinations
    - domain
    - title
    - 
- find Plagarism score for document (get Url)
  - get document from s3
  - convert it into pg vector with open ai embeddings
  - find similarity score with all other documents
  - return top 10 documents with similarity score

- Insert Project
  - Get all document data and put it into Database
  - Convert that into pg vector correspondingly and upload it to database
  
- qa bot endpoint
  - get question and answer from database



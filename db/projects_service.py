import csv
import ast

from db import db_client
from db.vector_utils import string_to_vector
from shared.resourcereader import get_absolute_path_from_resources








def create_projects_table():
    """Create the projects table if it doesn't exist."""
    try:
        print(db_client.get_conn())
        cursor = db_client.get_conn().cursor()

        create_table_query = """
        CREATE TABLE projects (
            id SERIAL PRIMARY KEY,
            short_summary TEXT,
            issue TEXT,
            issuevector Vector(768),
            conversationvector Vector(768),
            resolution TEXT,
            next_steps TEXT,
            sentiment TEXT,
            agent_performance TEXT,
            date_created TIMESTAMP DEFAULT NOW(),
            tags TEXT[]
        )"""

        cursor.execute(create_table_query)
        db_client.get_conn().commit()

        cursor.close()

        print("Table projects created successfully!")
    except Exception as e:
        print(f"Error creating table: {e}")



def get_row_as_json(row, keys):
    master_list = []
    for key in keys:
        raw_value = row.get(key, None)
        if raw_value:
            tags_list = ast.literal_eval(raw_value)
            normalized_tags = [] ## [normalize_tag(tag) for tag in tags_list]
            master_list.extend(normalized_tags)

    return master_list



# init postgres db client
def ensure_projects_exists():

    
    if 1 == 1:
        return

    if db_client.check_table_exists("projects"):
        return

    create_projects_table()
    cursor = db_client.get_conn().cursor()

    # Read and insert data from CSV
    with open(get_absolute_path_from_resources("data/formatted_week_0612_summaries.csv"), 'r') as f:
        reader = csv.DictReader(f)

        index = 0
        for row in reader:
            index += 1
            # if index == 100:
            #     break
            #exit for if index is 10


            try:
                # row['Tags'] = get_row_as_json(row,"Tags")
                # row['Product_Name'] = get_row_as_json(row,"Product_Name")
                issuevector = string_to_vector(row['issue'])
                tags = get_row_as_json(row,["Tags","Product_Name"])


                cursor.execute("""
                           INSERT INTO projects (
    short_summary, issue, resolution, 
    next_steps, sentiment, agent_performance, 
    date_created, tags,  issuevector
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                         """, (
                    row['title'],
                    row['issue'],
                    row['resolution'],
                    row['next_steps'],
                    row['sentiment'],
                    row['agent_performance'],
                    row['time_of_call'],
                    tags,
                    issuevector

                ))


            except Exception as e:
                print(f"Error inserting row: {e} {row}")
                raise
            db_client.get_conn().commit()

    # Commit the transaction


    # Close the cursor and db_client.get_conn()ection
    cursor.close()
    print("Data inserted successfully!")






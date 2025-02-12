from openai import AzureOpenAI

from typing import Annotated

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from config import config
from databases.sql_service import get_db_connection

import logging

class ChatWithDataPlugin:
    def get_openai_client(self) -> AzureOpenAI:
        """
        Get the OpenAI client
        """
        try:
            client = AzureOpenAI(
                azure_endpoint = config.AZURE_OPENAI_ENDPOINT,
                azure_deployment= config.AZURE_OPENAI_DEPLOYMENT_MODEL,
                api_key = config.AZURE_OPENAI_API_KEY,
                api_version = config.AZURE_OPENAI_API_VERSION
            )
            return client
        except Exception as e:
            logging.error(f"Error getting OpenAI client: {e}", exc_info=True)
            raise

    @kernel_function(name="Greeting", description="Respond to any greeting or general questions")
    def greeting(self, input: Annotated[str, "the question"]) -> Annotated[str, "The output is a string"]:
        # query = input.split(':::')[0]
        query = input

        client = self.get_openai_client()

        try:
            completion = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant to repond to any greeting or general questions."},
                    {"role": "user", "content": query},
                ],
                temperature=0,
            )
            answer = completion.choices[0].message.content
        except Exception as e:
            answer = str(e) # 'Information from database could not be retrieved. Please try again later.'
        return answer

    
    @kernel_function(name="ChatWithSQLDatabase", description="Given a query, get details from the database")
    def get_SQL_Response(
        self,
        input: Annotated[str, "the question"]
        ):
        
        # clientid = input.split(':::')[-1]
        # query = input.split(':::')[0] + ' . ClientId = ' + input.split(':::')[-1]
        # clientid = ClientId
        query = input

        client = self.get_openai_client()

        sql_prompt = f'''A valid T-SQL query to find {query} for tables and columns provided below:
        1. Table: km_processed_data
        Columns: ConversationId,EndTime,StartTime,Content,summary,satisfied,sentiment,topic,keyphrases,complaint
        2. Table: processed_data_key_phrases
        Columns: ConversationId,key_phrase,sentiment
        Use ConversationId as the primary key in tables for queries but not for any other operations.
        Only return the generated sql query. do not return anything else.''' 
        try:

            completion = client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": sql_prompt},
                ],
                temperature=0,
            )
            sql_query = completion.choices[0].message.content
            sql_query = sql_query.replace("```sql",'').replace("```",'')
            #print(sql_query)
        
            # connectionString = os.environ.get("SQLDB_CONNECTION_STRING")

            conn = get_db_connection()
            # conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            cursor.close()
            conn.close()

            answer = ''
            for row in cursor.fetchall():
                answer += str(row)
        except Exception as e:
            answer = str(e) # 'Information from database could not be retrieved. Please try again later.'
        return answer
        #return sql_query

    
    @kernel_function(name="ChatWithCallTranscripts", description="given a query, get answers from search index")
    def get_answers_from_calltranscripts(
        self,
        question: Annotated[str, "the question"]
    ):

        search_endpoint = config.AZURE_AI_SEARCH_ENDPOINT
        search_key = config.AZURE_AI_SEARCH_API_KEY
        index_name = config.AZURE_AI_SEARCH_INDEX

        client = self.get_openai_client()

        query = question
        system_message = '''You are an assistant who provides an analyst with helpful information about data. 
        You have access to the call transcripts, call data, topics, sentiments, and key phrases.
        You can use this information to answer questions.
        If you cannot answer the question, always return - I cannot answer this question from the data available. Please rephrase or add more details.'''
        answer = ''
        try:
            completion = client.chat.completions.create(
                model = config.AZURE_OPENAI_DEPLOYMENT_MODEL,
                messages = [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                seed = 42,
                temperature = 0,
                max_tokens = 800,
                extra_body = {
                    "data_sources": [
                        {
                            "type": "azure_search",
                            "parameters": {
                                "endpoint": search_endpoint,
                                "index_name": index_name,
                                "semantic_configuration": "default",
                                "query_type": "vector_simple_hybrid", #"vector_semantic_hybrid"
                                "fields_mapping": {
                                    "content_fields_separator": "\n",
                                    "content_fields": ["content"],
                                    "filepath_field": "chunk_id",
                                    "title_field": "", #null,
                                    "url_field": "sourceurl",
                                    "vector_fields": ["contentVector"]
                                },
                                "semantic_configuration": 'my-semantic-config',
                                "in_scope": "true",
                                "role_information": system_message,
                                # "vector_filter_mode": "preFilter", #VectorFilterMode.PRE_FILTER,
                                # "filter": f"client_id eq '{ClientId}'", #"", #null,
                                "strictness": 3,
                                "top_n_documents": 5,
                                "authentication": {
                                    "type": "api_key",
                                    "key": search_key
                                },
                                "embedding_dependency": {
                                    "type": "deployment_name",
                                    "deployment_name": "text-embedding-ada-002"
                                },

                            }
                        }
                    ]
                }
            )
            answer = completion.choices[0].message.content
        except:
            answer = 'Details could not be retrieved. Please try again later.'
        return answer

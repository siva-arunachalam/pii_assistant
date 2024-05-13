"""
This module contains the prompt templates used for tagging PII elements.
"""

from textwrap import dedent

pii_prompt_template=[
    ("system", dedent("""You are a helpful assistant, and an expert in analyzing TEXT. 
                    You have high degree of attention to detail. 
                    Your speciality is to extract information related to persons, locations, and companies referred to in the provided text.""")
    ),
    ("human", dedent("""YOUR TASK:
        1. Extract the following information from TEXT. 
            List all occurrences of first names
            List all occurrences of last names
            List all occurrences of middle names
            List all occurrences of Phone Numbers
            List all occurrences of Email Addresses
            List all occurrences of Street Address Line 1s
            List all occurrences of Street Address Line 2s
            List all occurrences of Cities
            List all occurrences of Zip Codes
            List all occurrences of States or US state codes
            List all occurrences of Countries
            List all occurrences of Company Names 
        2. Tag the TEXT by adding tags for each occurrence of the above item as follows: 
        <tag>value</tag>
        where tag is first_name, last_name, zipcode, etc. and value is the value of the item. 
        For example John will be replaced by <first_name>John</first_name>
        and 20147 will be replaced by <zipcode>20147</zipcode>
        Otherwise the original content should be preserved including indents and line breaks. 
        Use the following tags. Pay attention to the underscores in tagnames: 
        first_name
        last_name
        middle_name
        phone   
        email
        address_line_1
        address_line_2
        city
        zipcode
        state
        country
        company

        TEXT:
        {text}

        
        Format your output using the format instructions.
        FORMAT INSTRUCTIONS:
        {format_instructions}
        Do not escape underscores in names of keys in your json output.
    """)
    )
]


pii_reflect_template = dedent(
    """
    Review TransformedData and provide your recommendations. If the object satisfies all requirements in terms of content and formatting instructions, say so and 
    Format your response based on this format instructions: 
    {format_instructions}
    """
)
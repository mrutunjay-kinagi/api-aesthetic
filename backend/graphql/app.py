from flask import Flask
from flask_graphql import GraphQLView
from schema import schema

app = Flask(__name__)

# Setup GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enables the GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5003)  # Change port as needed

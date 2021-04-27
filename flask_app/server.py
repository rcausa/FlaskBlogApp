from flask import Flask, request, jsonify
from sqlite3 import Connection as SQLite3Connection
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
import linked_list, hash_table, binary_search_tree, custom_q, stack
import random

# app
app = Flask(__name__)

# app configuration dictionary
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlitedb.file"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0 

# In Object Relational Model (ORM): Classes (objects) become User database tables
# i.e. turns objects (OOP) into SQL statements

# configure sqlite3 to enforce foreign key constraints
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, SQLite3Connection):
	if isinstance(dbapi_connection, type(SQLite3Connection)):
		cursor = dbapi_connection.cursor()
		cursor.execute("PRAGMA foreign_keys=ON;")
		cursor.close()

# create database: pass app into SQLAlmchemy class, connects SQL->ORM->application
db = SQLAlchemy(app)
now = datetime.now()

# user tables
class User(db.Model):
	"""
	Creates a User table using SQLAlchemy.
	Each instance of a user contains four columns/attributes.
	"""
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	email = db.Column(db.String(50))
	address = db.Column(db.String(200))
	phone = db.Column(db.String(50))
	# Due to foreign key constraint, need to delete blog posts if user deleted
	posts = db.relationship("BlogPost", cascade='all, delete')
	

class BlogPost(db.Model):
	__tablename__ = "blog_post"
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50))
	body = db.Column(db.String(200))
	date = db.Column(db.Date)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	
# create routes for the API
# when URL has '/user' appended, and using POST method, route to this function
@app.route("/user", methods=['POST'])
def create_user():
	data = request.get_json()
	new_user = User(
		name = data["name"],
		email = data["email"],
		address = data["address"],
		phone = data["phone"]
	)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'message': "User created"}), 200


@app.route("/user/descending_id", methods=['GET'])
def get_all_users_descending():
	"""
	Query Users table, add users to a linked list.
	Return a descending array using jsonify.
	"""
	# 'query_all()' gives users with id in ascending order
	# Each user inserted at beginning, so order becomes descending
	users = User.query.all() 
	# instance of an empty linked list	
	all_users_ll = linked_list.LinkedList()

	for user in users:
		all_users_ll.insert_beginning(
			{
				"id" : user.id,
				"name" : user.name,
				"email" : user.email,
				"address" : user.address,
				"phone" : user.phone
			}
		)
	return jsonify(all_users_ll.to_list()), 200


@app.route("/user/ascending_id", methods=['GET'])
def get_all_users_ascending():
	"""
	Query Users table, add users to a linked list.
	Return an ascending array using jsonify.
	"""
	# Gives users with id in ascending order
	# Each user inserted at end, so order is ascending
	users = User.query.all() 
	# instance of an empty linked list	
	all_users_ll = linked_list.LinkedList()

	for user in users:
		all_users_ll.insert_end(
			{
				"id" : user.id,
				"name" : user.name,
				"email" : user.email,
				"address" : user.address,
				"phone" : user.phone,
			}
		)
	return jsonify(all_users_ll.to_list()), 200

@app.route("/user/<user_id>", methods=['GET'])
def get_one_user(user_id):
	users = User.query.all()

	all_users_ll = linked_list.LinkedList()

	for user in users:
		all_users_ll.insert_beginning(
			{
				"id" : user.id,
				"name" : user.name,
				"email" : user.email,
				"address" : user.address,
				"phone" : user.phone,
			}
		)
	user = all_users_ll.get_user_by_id(user_id) # dictionary
	return jsonify(user), 200 # convert to dictionary


@app.route("/user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	db.session.delete(user)
	db.session.commit()
	return jsonify({}), 200

@app.route("/blog_post/<user_id>", methods=['POST'])
def create_blog_post(user_id):
	# send POST request using correct URL
	data = request.get_json()
	# check user exists first (first user with that id)
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({"message" : "user does not exist!"}), 400

	ht = hash_table.HashTable(10)
	
	ht.add_key_value("title", data["title"])
	ht.add_key_value("body", data["body"])
	ht.add_key_value("date", now)
	ht.add_key_value("user_id", user_id)

	new_blog_post = BlogPost(
		title = ht.get_value("title"),
		body = ht.get_value("body"),
		date = ht.get_value("date"),
		user_id = ht.get_value("user_id"),
	)
	db.session.add(new_blog_post)
	db.session.commit()
	return jsonify({"message" : "new blog post created"}), 200


@app.route("/blog_post/<blog_post_id>", methods=['GET'])
def get_one_blog_post(blog_post_id):
	blog_posts = BlogPost.query.all() #BlogPost is a database which we query
	# list of all posts, ascending, want to insert into BST
	# Want to search the BST using the unique blog_post_id
	# Make BST more balanced by randomising inserted blog posts
	bst = binary_search_tree.BinarySearchTree()

	for post in blog_posts:
		bst.insert({
			"id" : post.id,
			"title" : post.title,
			"body" : post.body,
			"user_id" : post.user_id,
		})
	post = bst.search(blog_post_id) # returns the post given the blog_post_id
	if not post:
		# if no id found
		return jsonify({"message": "post not found"})
	return jsonify(post)


@app.route("/blog_post/numeric_body", methods=['GET'])
def get_numeric_post_bodies():
	"""
	Go through each char is body, add all ascii values to create one integer summary.
	"""
	blog_posts = BlogPost.query.all()
	q = custom_q.Queue()

	#add posts to queue
	for post in blog_posts:
		q.enqueue(post)
	# process each queue until queue empty
	return_list = []
	for _ in range(len(blog_posts)):
		post = q.dequeue() #returns removed table entry (data in dictionary)
		numeric_body = 0
		for char in post.data.body:
			numeric_body += ord(char)
		post.data.body = numeric_body
		return_list.append({
			"id" : post.data.id,
			"title" : post.data.title,
			"body" : post.data.body,
			"user_id" : post.data.user_id,
		})
	return jsonify(return_list)


@app.route("/blog_post/delete_last_10", methods=['DELETE'])
def delete_last_10():
	blog_posts = BlogPost.query.all() # blogs in ascending order
	s = stack.Stack()

	for post in blog_posts:
		s.push(post) # each blog added to head of stack, so last blog post = 'top' by the end

	for _ in range(10):
		post_to_delete = s.pop()
		db.session.delete(post_to_delete.data) # delete the post's data. pop() returns a node
		db.session.commit()

	return jsonify({"message" : "Successfully deleted last 10 blog entries"}), 200




if __name__ == "__main__":
	app.run(debug=True)
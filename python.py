import os
import sys
import cx_Oracle
from flask import Flask, render_template, request, jsonify, flash, redirect, session
import codecs
import mysql.connector as sql;
import csv
import hashlib

def init_session(connection, requestedTag_ignored):
	cursor = connection.cursor()
	cursor.execute("""
		ALTER SESSION SET
		  TIME_ZONE = 'UTC'
		  NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI'""")
 
# start_pool(): starts the connection pool
def start_pool():
	pool_min = 4
	pool_max = 4
	pool_inc = 0
	pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT
 
	print("Connecting to", os.environ.get("PYTHON_CONNECTSTRING"))
 
	pool = cx_Oracle.SessionPool(user=os.environ.get("PYTHON_USERNAME"),
								 password=os.environ.get("PYTHON_PASSWORD"),
								 dsn=os.environ.get("PYTHON_CONNECTSTRING"),
								 min=pool_min,
								 max=pool_max,
								 increment=pool_inc,
								 threaded=True,
								 getmode=pool_gmd,
								 sessionCallback=init_session)
 
	return pool
def create_schema():

	connection = pool.acquire()
	cursor = connection.cursor()
	cursor.execute("""
		begin
		  begin
			execute immediate 'drop table demo';
			exception when others then
			  if sqlcode <> -942 then
				raise;
			  end if;
		  end;
 
		  execute immediate 'create table demo (
			   id        number generated by default as identity,
			   username varchar2(40))';
 
		  execute immediate 'insert into demo (username) values (''chris'')';
 
		  commit;
		end;""")
 
################################################################################
#
# Specify some routes
#
# The default route will display a welcome message:
#   http://127.0.0.1:8080/
#
# To insert a new user 'fred' you can call:
#    http://127.0.0.1:8080/post/fred
#
# To find a username you can pass an id, for example 1:
#   http://127.0.0.1:8080/user/1
#
 
app = Flask(__name__)
 
# Display a welcome message on the 'home' page
@app.route('/')
def index():
	return render_template ('blog/index.html', title = "SMART DSC-2022");
	#return "Welcome to the demo app"

# Add a new username
#
# The new user's id is generated by the DB and returned in the OUT bind
# variable 'idbv'.  As before, we leave closing the cursor and connection to
# the end-of-scope cleanup.
@app.route('/post/<string:username>')
def post(username):
	connection = pool.acquire()
	cursor = connection.cursor()
	connection.autocommit = True
	idbv = cursor.var(int)
	cursor.execute("""
		insert into demo (username)
		values (:unbv)
		returning id into :idbv""", [username, idbv])
	return 'Inserted {} with id {}'.format(username, idbv.getvalue()[0])
 
# Show the username for a given id
@app.route('/user/<int:id>')
def show_username(id):
	connection = pool.acquire()
	cursor = connection.cursor()
	cursor.execute("select username from demo where id = :idbv", [id])
	r = cursor.fetchone()
	return (r[0] if r else "Unknown user id")
 
################################################################################
#
# Initialization is done once at startup time
#
if __name__ == '__main__':
 
	# Start a pool of connections
	#pool = start_pool()
 
	# Create a demo table
	#create_schema()
 
	# Start a webserver
	app.run(port=int(os.environ.get('PORT', '8080')))
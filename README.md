# Social Network Graph Demo


When you think about a web application, a graph database doesn’t usually spring to mind. Instead, most people just take the familiar route of using an SQL database to store information. While this is perfectly acceptable for most use cases there are sometimes those that would see tremendous benefits by using a graph database.
In this tutorial, I will show you how to make a basic web application using Flask that stores all of its information in a graph database. To be more precise we are using Memgraph DB, an in-memory database that can easily handle a lot of information and perform read/write instructions quite quickly.<br /><br />
Our use case is a Social Network Graph (in the code referred to as **SNG** for convenience) representing users and the connections between them. Usually, such a graph would contain millions of nodes and edges and the algorithms that are performed on them don’t do well with data being stored in relational databases.<br /><br />

<p align="center">
   <img src="https://github.com/g-despot/images/blob/master/sng_demo_screenshot.png?raw=true" alt="Data Model" width="900"/>
<p/>
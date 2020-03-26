# dxml (beta)
dxml stands for dart xml which makes dart/flutter very similar to jsx

the following code is an example on how it works !, it uses almost
all the features of my converter so don't panic
```javascript
import 'package:flutter/material.dart';

void main() {
  runApp(DXMLDemoApp());
}

class DXMLDemoApp extends StatefulWidget {
	
	State<DXMLDemoApp> createState() => <_DXMLDemoApp/>;
}

class _DXMLDemoApp extends State<DXMLDemoApp> {
	
	bool isLoggedIn = false;
	Widget build(BuildContext context) {
		return (<MaterialApp>

		<home>

<DefaultTabController length={% 3 %}>
	<Scaffold>
		<appBar>
			<title>
				<Text>welcome to my App!</Text>
			</title>
			<actions x-list={% true %}>
				<IconButton x-value={% Icon(Icons.settings) %}  onPressed={%() => {}%}/>
			</actions>
			<bottom>
				<TabBar>
					<Tab text={% "tab 1" %} x-value={% Icon(Icons.directions_car) %}/>
					<Tab text={% "tab 2" %} x-value={% Icon(Icons.directions_transit) %}/>
					<Tab text={% "tab 3" %} x-value={% Icon(Icons.directions_bike) %}/>
				</TabBar>
			</bottom>
		</appBar>

		<body>
			<TabBarView>
				
				{| 
				isLoggedIn ? 
				<Center>
					<Text>welcome !</Text>
				</Center> : 

				<Column mainAxisAlignment={% MainAxisAlignment.center %}>
					<Text>please login to continue</Text>
					<RaisedButton onPressed={% () => {

					setState(() => isLoggedIn = true)

					} %}><Text>login</Text></RaisedButton>
				</Column> 
				|}
				<Center>
					<Text>it\'s good to be true</Text>
				</Center>
				<Center>
					<Text>nice to meet ya</Text>
				</Center>
			</TabBarView>
		</body>
	</Scaffold>
</DefaultTabController>

		</home>
		</MaterialApp>);
	}
}

```
![run time example](https://scontent-hbe1-1.xx.fbcdn.net/v/t1.15752-9/90815022_564735407725555_6191075123869515776_n.png?_nc_cat=108&_nc_sid=b96e70&_nc_ohc=Gx3iPUt0-MYAX9UB8Js&_nc_ht=scontent-hbe1-1.xx&oh=dc12c8a3622aa827c5e1eabfa9601a8c&oe=5EA13B5A)

## quick notes on usage until the complete documentations are released:

* the compiler is written in python and supports both python2 and python3
* the files uses these syntax are called dxml files and must have the `.dxml` extension
in order to make them recognized by the compiler
* to convert `dxml` to regular `dart` you should run the following command
`python converter.py <path>` 
* dxml files must be compiled to pure dart files in order to run !
* the path is the path of the directory containing dxml files
* any dxml file in sub folder will be compiled
* you are free to use full dart syntax
* you can import external dart files from dxml files, however when you need to import dxml
from dart files you should import them with `.dart` extension

# complete documentations will be released soon !

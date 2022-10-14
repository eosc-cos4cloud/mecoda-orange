# Installation Guide

1. Install Orange Data Mining platform through https://orangedatamining.com/download 
<img src="images/orange_installation.png" alt="orange_installation"/> 

    Click on “Download Orange”.

2. Open Orange from the menu in your computer, you will see something like this:
<img src="images/orange_canvas.png" alt="orange_canvas"/> 

3. Go to menu “Options” and select “Add-ons”:
<img src="images/orange_addons.png" alt="orange_addons"/> 

4. In the pop-up click on ***Add more…*** button on the top right. A search window will appear called ***Add add-on by name***. Write ***mecoda-orange*** in the search box and click on the ***Add*** button.
<img src="images/orange_add_more2.png" alt="orange_add_more"/> 

5. ***Mecoda Orange*** will be available in the list of packages for installation. Check the box besides the name.
<img src="images/orange_mecoda_package.png" alt="orange_mecoda_package"/> 

6. We will need other packages for this example, so we check the box of the package called ***Geo*** and ***Image Analytics*** also.
<img src="images/orange_other_packages.png" alt="orange_other_packages"/> 

7. After selecting these three packages, we will press **OK** to install them.

8. Orange will show a message because it needs to restart. We click on **OK**.
<img src="images/orange_reinicio.png" alt="orange_reinicio"/> 

9. Orange will be restarted and the interface will show our new installed packages on the left side column:
<img src="images/orange_interface_installed.png" alt="orange_interface_installed"/> 

*WARNING*: If MECODA doesn’t appear in the interface, close it and remove the *.cache/Orange* folder, because other previous installations could be made and have problems with the new one. Check if it is installed in the Options >> Add-ons and if not, install it again.


# Example of Use with Odour Collect widget

1. Click on the OdourCollect widget inside the MECODA package:
<img src="images/oc_widget.png" alt="oc_widget"/> 

2. The OdourCollect widget will appear on the white canvas:
<img src="images/oc_widget2.png" alt="oc_widget2"/> 

3. Double click on the Odour Collect widget to open the window to download the data:
<img src="images/oc_widget3.png" alt="oc_widget3"/> 

Here we can see all the filters available to Odour Collect observations. If we don’t change anything we will get all the data available from 2019 to today. Click on **Commit** to make the request for the data.

4. After pressing **Commit** the widget will connect with the API from Odour Collect website to fetch the data and make it available to use in inside Orange:
<img src="images/oc_widget4.png" alt="oc_widget4"/> 
Here we can see that 11.676 observations are downloaded.

5. How is this data? We can now inspect it using the Table widget. Put your mouse over the right side of the Odour Collect widget where a pointed curve appears. Drag this curve and you will see a line appear:
<img src="images/oc_widget5.png" alt="oc_widget5"/> 

6. If we let go of the mouse, a menu will appear at the end of the line:
<img src="images/oc_widget6.png" alt="oc_widget6"/> 
These are the widgets available to connect with our data. Every output of a widget can be connected as the input of another widget. 

7. Let’s select **Data Table** to see our data as a table:
<img src="images/oc_widget7.png" alt="oc_widget7"/> 

8. Our goal is to analyse greek instances, but we just have the location included as **latitude** and **longitude**.
<img src="images/oc_widget8.png" alt="oc_widget8"/> 

9. Let’s connect this data to a Choropleth Map to see the observations in every country:
<img src="images/oc_widget9.png" alt="oc_widget9"/> 

10. Let’s zoom in the map to see Europe closer and click on Greece to select the observations from this country:
<img src="images/oc_widget10.png" alt="oc_widget10"/> 

11. Once Greece is selected, the Choropleth Map will filter the data and get the selected one as output. Let’s check it connecting another Table widget to the output of this map:
<img src="images/oc_widget11.png" alt="oc_widget11"/> 

This Table has around 304 observations, not the 11.000 from the beginning. These are the Greek ones. We can now make our analysis connecting the widgets to this table.

<img src="images/oc_choropleth_detail.png" alt="oc_choropleth_detail"/> 

If we change the “Detail” option in the Choropleth Map we can also see the number in the different regions of Greece:

## Let’s answer some questions now:
* Which category of odors is the most prevalent in Greece? Use the **Pivot Table** widget:
<img src="images/oc_pivot.png" alt="oc_pivot_table"/> 

* In which year are there more odours recorded? Use the **Distributions** widget:
<img src="images/oc_year.png" alt="oc_year"/> 

* What day of the week the most odours are recorded? Use the **Distributions** widget / or the **Pivot Table** widget:
<img src="images/oc_distributions_weekday2.png" alt="oc_distributions_weekday"/> 

* Where are the odours registered inside Greece? Can we see the points on a map? Use **Geo Map** widget
<img src="images/oc_geo_map.png" alt="oc_geo_map"/> 

* Which category of odour has the worst hedonic tone? Use the **BoxPlot**
<img src="images/orange_boxplot.png" alt="orange_boxplot"/> 

* Which category of odours have the biggest intensity?
<img src="images/orange_boxplot2.png" alt="orange_boxplot2"/> 

    We can also see the intensity in every category using the **Violin Plot**:
<img src="images/orange_violinplot.png" alt="orange_violinplot"/> 

* Imagine you want to change a column, to update the weekday names from english to greek. You can use the **Edit domain** option.
<img src="images/oc_edit_domain.png" alt="oc_edit_domain"/> 

* And if you want to inspect the whole dataset, you can use **Feature Statistics**.
<img src="images/oc_feature_statistics.png" alt="oc_feature_statistics"/> 





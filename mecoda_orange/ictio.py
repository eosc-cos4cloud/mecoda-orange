from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame
import pandas as pd
import ictiopy

class IctioWidget(OWBaseWidget):
    
    # Widget's name as displayed in the canvas
    name = "Ictio Obs."

    # Short widget description
    description = "Get observations from Ictio, a mobile phone app created to register observations of caught fish in the Amazon basin"

    # An icon resource file path for this widget
    icon = "icons/ictio.png"

    # Priority in the section MECODA
    priority = 10

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    path = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()
        
        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, 'No observations fetched yet.')
        self.infob = gui.widgetLabel(info, '')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        self.path_line = gui.lineEdit(
            self.searchBox, 
            self, 
            "path", 
            label="Path to zip:", 
            orientation=1, 
            controlWidth=180,
            )

        gui.separator(self.searchBox)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Load", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')
    
    # function to change subtype items due to type choice

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'This could take a while, depending on connection speed.')
        try:
            # convert date_init and date_end to datetime format

            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            
            # construct GPScoords

            observations = ictiopy.load_zipdb(self.path) 

            if len(observations) > 0:
                
                table_ictio = table_from_frame(observations)

                self.infoa.setText(f'{len(observations)} observations gathered')
                self.info.set_output_summary(len(observations))

                self.Outputs.observations.send(table_ictio)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')
            
        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')
            
        progress.finish()    
        

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(IctioWidget).run()
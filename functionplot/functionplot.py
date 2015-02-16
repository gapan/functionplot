#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import gtk
import sys
import matplotlib.ticker
from matplotlib.figure import Figure
# alternative GTK/GTKAgg/GTKCairo backends
# Agg and Cairo have much improved rendering
#from matplotlib.backends.backend_gtk import FigureCanvasGTK \
#    as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg \
    as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo \
#    as FigureCanvas
from FunctionGraph import FunctionGraph

import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class CenteredFormatter(matplotlib.ticker.ScalarFormatter):
    """Acts exactly like the default Scalar Formatter, but yields an empty 
    label for ticks at the origin."""
    def __call__(self, value, pos=None):
        if value == 0:
            return ''
        else:
            return matplotlib.ticker.ScalarFormatter.__call__(self, value, pos)

class GUI:
    #
    # Main Window
    #

    # menu item activation signals
    def on_imagemenuitem_quit_activate(self, widget):
        gtk.main_quit()

    def on_checkmenuitem_legend_toggled(self, widget):
        self.fg.show_legend = self.checkmenuitem_legend.get_active()
        self.graph_update()
    
    def on_checkmenuitem_outliers_toggled(self, widget):
        self.fg.outliers = self.checkmenuitem_outliers.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    # toolbar button activation signals
    def on_btn_add_clicked(self, widget):
        self.entry_function.set_text('')
        self.dialog_add_function.show()
        self.entry_function.grab_focus()

    def on_btn_remove_clicked(self, widget):
        selected_line = self.treeview_functions.get_selection()
        self.ls_functions, iter = selected_line.get_selected()
        if iter is not None:
            index = self.ls_functions.get_value(iter, 3)
            self.fg.functions.pop(index)
            self.fg.calc_intercepts()
            self.update_function_list()
            self.graph_update()

    def on_btn_zoom_x_in_clicked(self, widget):
        self.fg.zoom_x_in()
        self.graph_update()
    
    def on_btn_zoom_x_out_clicked(self, widget):
        self.fg.zoom_x_out()
        self.graph_update()

    def on_btn_zoom_y_in_clicked(self, widget):
        self.fg.zoom_y_in()
        self.graph_update()
    
    def on_btn_zoom_y_out_clicked(self, widget):
        self.fg.zoom_y_out()
        self.graph_update()
    
    def on_btn_zoomin_clicked(self, widget):
        self.fg.zoom_in()
        self.graph_update()

    def on_btn_zoomout_clicked(self, widget):
        self.fg.zoom_out()
        self.graph_update()
   
    def on_btn_auto_toggled(self, widget):
        self.fg.auto = self.btn_auto.get_active()
        if self.fg.auto:
            self.fg.zoom_default()
            self.graph_update()

    # toggle visibility in function list
    def on_cr_toggle_visible_toggled(self, widget, event):
        i = int(event)
        visible = self.fg.functions[i].visible
        if visible:
            self.fg.functions[i].visible = False
        else:
            self.fg.functions[i].visible = True
        self.update_function_list()
        self.graph_update()

    # zoom in/out with the mouse wheel
    def wheel_zoom(self, event):
        if event.button == 'down':
            self.fg.zoom_out()
        elif event.button == 'up':
            self.fg.zoom_in()
        self.graph_update()
    # pan handling
    # when pressing down the mouse button on the graph, record
    # the current mouse coordinates
    def pan_press(self, event):
        if event.inaxes != self.ax: return
        self.mousebutton_press = event.xdata, event.ydata

    # when releasing the mouse button, stop recording the
    # mouse coordinates and redraw
    def pan_release(self, event):
        self.mousebutton_press = None
        self.graph_update()

    # when moving the mouse, while holding down the mouse button (any
    # mouse button - that makes nice middle-click pan and zoom possible)
    # calculate how much the mouse has travelled and adjust the graph
    # accordingly
    def pan_motion(self, event):
        if self.mousebutton_press is None: return
        if event.inaxes != self.ax: return
        self.fg.auto = False
        old_x, old_y = self.mousebutton_press
        dx = event.xdata - old_x
        dy = event.ydata - old_y
        self.fg.x_min -= dx
        self.fg.x_max -= dx
        self.fg.y_min -= dy
        self.fg.y_max -= dy
        self.fg.update_graph_points()
        self.graph_update()

    # update the graph
    def graph_update(self):
        self.ax.clear()
        
        if self.fg.auto:
            self.fg.update_xylimits()
        x_min, x_max = self.fg.x_min, self.fg.x_max
        y_min, y_max = self.fg.y_min, self.fg.y_max
       
        # put axes in center instead of the sides
        # when axes are off screen, put them on the edges
        self.ax.grid(True)
        if x_min < 0 and x_max >0:
            self.ax.spines['left'].set_color('black')
            self.ax.spines['left'].set_position(('data', 0))
            self.ax.spines['left'].set_smart_bounds(False)
            self.ax.spines['right'].set_color('none')
            self.ax.yaxis.set_ticks_position('left')
        elif x_min >= 0:
            self.ax.spines['left'].set_color('black')
            self.ax.spines['left'].set_position(('data', x_min))
            self.ax.spines['left'].set_smart_bounds(False)
            self.ax.spines['right'].set_color('none')
            self.ax.yaxis.set_ticks_position('left')
        else:
            self.ax.spines['right'].set_color('black')
            self.ax.spines['right'].set_position(('data', x_max))
            self.ax.spines['right'].set_smart_bounds(False)
            self.ax.spines['left'].set_color('none')
            self.ax.yaxis.set_ticks_position('right')
        if y_min < 0 and y_max >0:
            self.ax.spines['bottom'].set_color('black')
            self.ax.spines['bottom'].set_position(('data', 0))
            self.ax.spines['bottom'].set_smart_bounds(False)
            self.ax.spines['top'].set_color('none')
            self.ax.xaxis.set_ticks_position('bottom')
        elif y_min >= 0:
            self.ax.spines['bottom'].set_color('black')
            self.ax.spines['bottom'].set_position(('data', y_min))
            self.ax.spines['bottom'].set_smart_bounds(False)
            self.ax.spines['top'].set_color('none')
            self.ax.xaxis.set_ticks_position('bottom')
        else:
            self.ax.spines['top'].set_color('black')
            self.ax.spines['top'].set_position(('data', y_max))
            self.ax.spines['top'].set_smart_bounds(False)
            self.ax.spines['bottom'].set_color('none')
            self.ax.xaxis.set_ticks_position('top')

        # we don't need the origin annotated in both axes
        if x_min < 0 and x_max >0 and y_min < 0 and y_max > 0:
            formatter = CenteredFormatter()
            formatter.center = 0
            self.ax.xaxis.set_major_formatter(formatter)
            self.ax.yaxis.set_major_formatter(formatter)
            self.ax.annotate('(0,0)', (0, 0), xytext=(-4, -4),
                    textcoords='offset points', ha='right', va='top')

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        legend = []

        for f in self.fg.functions:
            x, y = f.graph_points
            if f.visible:
                color=self.color[len(legend) % len(self.color)]
                self.ax.plot(x, y, linewidth=2, color=color)
                xp = []
                yp = []
                for p in f.poi:
                    # don't plot discontinuity points here
                    if p.point_type < 6:
                        #FIXME: if point type enabled
                        xp.append(p.x)
                        yp.append(p.y)
                    self.ax.scatter(xp, yp, s=80, c=color, linewidths=0)
                # plot discontinuity points now
                xp = []
                yp = []
                for p in f.poi:
                    if p.point_type == 6:
                        xp.append(p.x)
                        yp.append(p.y)
                    self.ax.scatter(xp, yp, s=80, marker='x', c=color, 
                            linewidths=2)
                # add function to legend
                legend.append(f.mathtex_expr)
        xp = []
        yp = []
        # add function intercepts POI
        for p in self.fg.poi:
            xp.append(p.x)
            yp.append(p.y)
        self.ax.scatter(xp, yp, s=80, alpha=0.5, c='black',
                linewidths=0)
        if self.fg.show_legend:
            self.ax.legend(legend, loc='upper right', bbox_to_anchor=(1,1))
        self.ax.figure.canvas.draw()
        # check/uncheck the toolbutton for auto-adjustment
        self.btn_auto.set_active(self.fg.auto)

    def update_function_list(self):
        self.ls_functions.clear()
        visible_functions = 0
        index = 0
        for f in self.fg.functions:
            if f.visible:
                color = self.color[visible_functions % len(self.color)]
                visible_functions += 1
            else:
                color = '#999999'
            self.ls_functions.append([f.visible, f.expr+'',
                gtk.gdk.Color(color), index])
            index += 1

    def gtk_main_quit(self, widget, data=None):
        gtk.main_quit()

    #
    # Add function dialog
    #
    def on_dialog_add_function_delete_event(self, widget, event):
        self.dialog_add_function.hide()
        return True

    def _entry_function_append_text(self, text):
        t = self.entry_function.get_text()
        t = t+text
        l = len(t)
        self.entry_function.set_text(t)
        self.entry_function.grab_focus()
        self.entry_function.set_position(l)

    def on_button_1_clicked(self, widget):
        self._entry_function_append_text('1')

    def on_button_2_clicked(self, widget):
        self._entry_function_append_text('2')

    def on_button_3_clicked(self, widget):
        self._entry_function_append_text('3')

    def on_button_4_clicked(self, widget):
        self._entry_function_append_text('4')

    def on_button_5_clicked(self, widget):
        self._entry_function_append_text('5')

    def on_button_6_clicked(self, widget):
        self._entry_function_append_text('6')

    def on_button_7_clicked(self, widget):
        self._entry_function_append_text('7')

    def on_button_8_clicked(self, widget):
        self._entry_function_append_text('8')

    def on_button_9_clicked(self, widget):
        self._entry_function_append_text('9')

    def on_button_0_clicked(self, widget):
        self._entry_function_append_text('0')

    def on_button_x_clicked(self, widget):
        self._entry_function_append_text('x')

    def on_button_plus_clicked(self, widget):
        self._entry_function_append_text('+')

    def on_button_minus_clicked(self, widget):
        self._entry_function_append_text('-')

    def on_button_times_clicked(self, widget):
        self._entry_function_append_text('*')

    def on_button_div_clicked(self, widget):
        self._entry_function_append_text('/')

    def on_button_sin_clicked(self, widget):
        self._entry_function_append_text('sin(x)')

    def on_button_cos_clicked(self, widget):
        self._entry_function_append_text('cos(x)')

    def on_button_tan_clicked(self, widget):
        self._entry_function_append_text('tan(x)')
    
    def on_button_cot_clicked(self, widget):
        self._entry_function_append_text('cot(x)')
    
    def on_button_sec_clicked(self, widget):
        self._entry_function_append_text('sec(x)')

    def on_button_csc_clicked(self, widget):
        self._entry_function_append_text('csc(x)')

    def on_button_log_clicked(self, widget):
        self._entry_function_append_text('log(x)')

    def on_button_ln_clicked(self, widget):
        self._entry_function_append_text('ln(x)')

    def on_button_10p_x_clicked(self, widget):
        self._entry_function_append_text('10^x')

    def on_button_ep_x_clicked(self, widget):
        self._entry_function_append_text('e^x')

    def on_button_sqrt_clicked(self, widget):
        self._entry_function_append_text('sqrt(x)')

    def on_button_abs_clicked(self, widget):
        self._entry_function_append_text('abs(x)')

    def on_button_power2_clicked(self, widget):
        self._entry_function_append_text('x^2')
    
    def on_button_power3_clicked(self, widget):
        self._entry_function_append_text('x^3')

    def on_button_pi_clicked(self, widget):
        self._entry_function_append_text('pi')

    def on_button_e_clicked(self, widget):
        self._entry_function_append_text('e')

    def on_button_addf_cancel_clicked(self, widget):
        self.dialog_add_function.hide()

    def on_button_addf_ok_clicked(self, widget):
        expr = self.entry_function.get_text()
        f = self.fg.add_function(expr)
        if f:
            self.dialog_add_function.hide()
            self.update_function_list()
            self.graph_update()
        else:
            self.dialog_add_error.show()

    # Error while adding function dialog
    def on_dialog_add_error_delete_event(self, widget, event):
        self.dialog_add_error.hide()
        return True

    def on_button_add_error_close_clicked(self, widget):
        self.dialog_add_error.hide()

    def __init__(self):
        # Only a few colors defined. Hard to find more that will stand out.
        # If there are more functions, colors will cycle from the start
        # colors were taken from http://latexcolor.com/
        self.color = ['#4F81BD', # blue
                '#C0504D',# red
                '#9BBB59',# green
                '#8064A2',# purple
                '#F79646',# orange
                '#00B7EB',# cyan
                '#3B444B',# charcoal
                '#F0E130',# yellow
                '#DE5D83',# pink (blush)
                '#B87333',# copper
                '#0047AB',# cobalt
                '#614051',# eggplant
                ]
        
        # create a FunctionGraph object
        self.fg = FunctionGraph()
       
        # we'll need this for panning
        self.mousebutton_press = None
        
        # Load GUI from glade file
        builder = gtk.Builder()
        builder.add_from_file('functionplot.glade')
        
        #
        # Main Window
        #
        self.window = builder.get_object('functionplot')
        #self.window.maximize()
        # menus
        self.imagemenuitem_quit = \
            builder.get_object('imagemenuitem_quit')
        self.checkmenuitem_legend = builder.get_object('checkmenuitem_legend')
        self.checkmenuitem_legend.set_active(self.fg.show_legend)
        # main toolbar
        self.btn_auto = builder.get_object('btn_auto')
        self.btn_auto.set_active(self.fg.auto)
        self.checkmenuitem_outliers = \
            builder.get_object('checkmenuitem_outliers')
        self.checkmenuitem_outliers.set_active(self.fg.outliers)
        # graph in main window
        self.table = builder.get_object('table_graph')
        self.fig = Figure(facecolor='w', tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.table.attach(self.canvas, 0, 1, 0, 1)
        # function list
        self.ls_functions = builder.get_object('liststore_functions')
        self.ls_functions.clear()
        self.treeview_functions = builder.get_object('treeview_functions')
        self.cr_toggle_visible = builder.get_object('cr_toggle_visible')
        # catch mouse wheel scroll
        self.canvas.mpl_connect('scroll_event', self.wheel_zoom)
        # catch click and pan
        self.canvas.mpl_connect('button_press_event', self.pan_press)
        self.canvas.mpl_connect('button_release_event', self.pan_release)
        self.canvas.mpl_connect('motion_notify_event', self.pan_motion)
        self.graph_update()
        
        #
        # Add function dialog
        #
        self.dialog_add_function = builder.get_object('dialog_add_function')
        self.entry_function = builder.get_object('entry_function')
        self.dialog_add_error = builder.get_object('dialog_add_error')

        # Connect all signals
        builder.connect_signals(self)
        self.window.show_all()

if __name__ == "__main__":
    app = GUI()
    gtk.main()

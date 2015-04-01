#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import gtk
import sys
import threading
import pickle
import os
import matplotlib.ticker
from matplotlib.figure import Figure
# alternative GTK/GTKAgg/GTKCairo backends
# Agg and Cairo have much improved rendering
#from matplotlib.backends.backend_gtk import FigureCanvasGTK \
#    as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg \
    as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import \
#    FigureCanvasGTKCairo as FigureCanvas
from FunctionGraph import FunctionGraph

import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
        format='(%(processName)-10s) %(message)s',)

# Internationalization
import locale
import gettext
import gtk.glade
gettext.bindtextdomain("functionplot", "/usr/share/locale")
gettext.textdomain("functionplot")
gettext.install("functionplot", "/usr/share/locale", unicode=1)
gtk.glade.bindtextdomain("functionplot", "/usr/share/locale")
gtk.glade.textdomain("functionplot")

#Initializing the gtk's thread engine
gtk.gdk.threads_init()

# Use the stix fonts for matplotlib mathtext.
# They blend better with Times New Roman.
matplotlib.rcParams['mathtext.fontset'] = 'stix'

def threaded(f):
    def wrapper(*args):
        t = threading.Thread(target=f, args=args)
        t.start()
    return wrapper

class CenteredFormatter(matplotlib.ticker.ScalarFormatter):
    """Acts exactly like the default Scalar Formatter, but yields an
    empty label for ticks at the origin."""
    def __call__(self, value, pos=None):
        if value == 0:
            return ''
        else:
            return matplotlib.ticker.ScalarFormatter.__call__(self,
                    value, pos)

class GUI:
    #
    # Main Window
    #

    # menu item activation signals

    def on_imagemenuitem_file_save_as_activate(self, widget):
        self.fcdialog_save.set_current_folder(self.folder)
        self.fcdialog_save.show()

    def on_imagemenuitem_export_activate(self, widget):
        self.fcdialog_export.set_current_folder(self.folder)
        self.fcdialog_export.show()

    def on_imagemenuitem_quit_activate(self, widget):
        gtk.main_quit()

    # View menu

    def on_checkmenuitem_function_intersections_toggled(self, widget):
        self.fg.point_type_enabled[1] = \
                self.checkmenuitem_function_intersections.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_x_intercepts_toggled(self, widget):
        self.fg.point_type_enabled[2] = \
                self.checkmenuitem_x_intercepts.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_y_intercepts_toggled(self, widget):
        self.fg.point_type_enabled[3] = \
                self.checkmenuitem_y_intercepts.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_extrema_toggled(self, widget):
        self.fg.point_type_enabled[4] = \
                self.checkmenuitem_extrema.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_inflection_toggled(self, widget):
        self.fg.point_type_enabled[5] = \
                self.checkmenuitem_inflection.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_vertical_asym_toggled(self, widget):
        self.fg.point_type_enabled[6] = \
                self.checkmenuitem_vertical_asym.get_active()
        self.fg.update_xylimits()
        self.graph_update()
    
    def on_checkmenuitem_horizontal_asym_toggled(self, widget):
        self.fg.point_type_enabled[7] = \
                self.checkmenuitem_horizontal_asym.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_slope45_toggled(self, widget):
        self.fg.point_type_enabled[8] = \
                self.checkmenuitem_slope45.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_outliers_toggled(self, widget):
        self.fg.outliers = self.checkmenuitem_outliers.get_active()
        self.fg.update_xylimits()
        self.graph_update()

    def on_checkmenuitem_show_poi_toggled(self, widget):
        self.fg.show_poi = self.checkmenuitem_show_poi.get_active()
        self.graph_update()

    def on_checkmenuitem_legend_toggled(self, widget):
        self.fg.show_legend = self.checkmenuitem_legend.get_active()
        self.graph_update()

    # toolbar button activation signals
    def on_btn_new_clicked(self, widget):
        if self.changed:
            self.dialog_confirm_new.show()
        else:
            self.changed = False
            self.filename = None
            self.export_filename = None
            self.fg.new()
            self.update_function_list()
            self.graph_update()
    
    def on_btn_open_clicked(self, widget):
        if self.changed:
            self.dialog_confirm_open.show()
        else:
            self.fcdialog_open.set_current_folder(self.folder)
            self.fcdialog_open.show()

    def on_btn_save_clicked(self, widget):
        if self.filename is None:
            self.fcdialog_save.set_current_folder(self.folder)
            self.fcdialog_save.show()
        else:
            self._save()
            self.changed = False
    
    def on_btn_add_clicked(self, widget):
        self.changed = True
        self.entry_function.set_text('')
        self.dialog_add_function.show()
        self.entry_function.grab_focus()

    def on_btn_remove_clicked(self, widget):
        selected_line = self.treeview_functions.get_selection()
        self.ls_functions, iter = selected_line.get_selected()
        if iter is not None:
            index = self.ls_functions.get_value(iter, 3)
            self.fg.functions.pop(index)
            self.fg.calc_intersections()
            self.update_function_list()
            self.graph_update()
            self.changed = True

    def on_btn_zoom_x_in_clicked(self, widget):
        self.changed = True
        self.fg.zoom_x_in()
        self.graph_update()
    
    def on_btn_zoom_x_out_clicked(self, widget):
        self.changed = True
        self.fg.zoom_x_out()
        self.graph_update()

    def on_btn_zoom_y_in_clicked(self, widget):
        self.changed = True
        self.fg.zoom_y_in()
        self.graph_update()
    
    def on_btn_zoom_y_out_clicked(self, widget):
        self.changed = True
        self.fg.zoom_y_out()
        self.graph_update()
    
    def on_btn_zoomin_clicked(self, widget):
        self.changed = True
        self.fg.zoom_in()
        self.graph_update()

    def on_btn_zoomout_clicked(self, widget):
        self.changed = True
        self.fg.zoom_out()
        self.graph_update()
   
    def on_btn_auto_toggled(self, widget):
        self.changed = True
        self.fg.auto = self.btn_auto.get_active()
        if self.fg.auto:
            self.fg.zoom_default()
            self.graph_update()

    # toggle visibility in function list
    def on_cr_toggle_visible_toggled(self, widget, event):
        self.changed = True
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
        self.changed = True
        if event.button == 'down':
            self.fg.zoom_out()
        elif event.button == 'up':
            self.fg.zoom_in()
        self.graph_update()
    # pan handling
    # when pressing down the mouse button on the graph, record
    # the current mouse coordinates
    def pan_press(self, event):
        self.changed = True
        if event.inaxes != self.ax: return
        self.mousebutton_press = event.xdata, event.ydata

    # when releasing the mouse button, stop recording the
    # mouse coordinates and redraw
    def pan_release(self, event):
        self.mousebutton_press = None
        self.graph_update()

    # when moving the mouse, while holding down the mouse button (any
    # mouse button - that makes nice middle-click pan and zoom
    # possible) calculate how much the mouse has travelled and adjust
    # the graph accordingly
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

        self.ax.set_xlim(float(x_min), float(x_max))
        self.ax.set_ylim(float(y_min), float(y_max))
        legend = []

        for f in self.fg.functions:
            x, y = f.graph_points
            if f.visible:
                color=self.color[len(legend) % len(self.color)]
                self.ax.plot(x, y, linewidth=2, color=color)
                xp = []
                yp = []
                if self.fg.show_poi:
                    for p in f.poi:
                        # don't plot vertical or horizontal asymptotes
                        # here. We'll do it later
                        if p.point_type < 6 or p.point_type > 7:
                            if self.fg.point_type_enabled[p.point_type]:
                                xp.append(p.x)
                                yp.append(p.y)
                        self.ax.scatter(xp, yp, s=80, c=color,
                                linewidths=0)
                    # plot asymptotes now
                    xp = []
                    yp = []
                    for p in f.poi:
                        if p.point_type == 6:
                            if self.fg.point_type_enabled[p.point_type]:
                                xp.append(p.x)
                                yp.append(0)
                            # vertical asymptotes are plotted as 'x'
                            self.ax.scatter(xp, yp, s=80, marker='x',
                                    c=color, linewidths=2)
                    xp = []
                    yp = []
                    for p in f.poi:
                        if p.point_type == 7:
                            if self.fg.point_type_enabled[p.point_type]:
                                xp.append(0)
                                yp.append(p.y)
                            # horizontal asymptotes are plotted as '+'
                            self.ax.scatter(xp, yp, s=80, marker='+',
                                    c=color, linewidths=2)
                # add function to legend
                legend.append(f.mathtex_expr)
        if self.fg.show_poi:
            xp = []
            yp = []
            # add function intercepts POI
            for p in self.fg.poi:
                if self.fg.point_type_enabled[p.point_type]:
                    xp.append(p.x)
                    yp.append(p.y)
            self.ax.scatter(xp, yp, s=80, alpha=0.5, c='black',
                    linewidths=0)
        if self.fg.show_legend:
            self.ax.legend(legend, loc='upper right',
                    bbox_to_anchor=(1,1), fontsize=18)
        self.ax.figure.canvas.draw()
        # check/uncheck the toolbutton for auto-adjustment
        self.btn_auto.set_active(self.fg.auto)

    def update_function_list(self):
        self.ls_functions.clear()
        visible_functions = 0
        index = 0
        for f in self.fg.functions:
            if f.visible:
                color = self.color[visible_functions % \
                        len(self.color)]
                visible_functions += 1
            else:
                color = '#999999'
            self.ls_functions.append([f.visible, f.expr.lower()+'',
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
        self._entry_function_append_text('exp(x)')

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

    @threaded
    def on_button_addf_ok_clicked(self, widget):
        gtk.gdk.threads_enter()
        self.window_calculating.show()
        gtk.gdk.threads_leave()
        expr = self.entry_function.get_text()
        f = self.fg.add_function(expr)
        if f:
            gtk.gdk.threads_enter()
            self.dialog_add_function.hide()
            self.window_calculating.hide()
            self.update_function_list()
            self.graph_update()
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.window_calculating.hide()
            self.dialog_add_error.show()
            gtk.gdk.threads_leave()

    # Error while adding function dialog
    def on_dialog_add_error_delete_event(self, widget, event):
        self.dialog_add_error.hide()
        return True

    def on_button_add_error_close_clicked(self, widget):
        self.dialog_add_error.hide()

    #
    # file new/open/save dialogs
    #
    def on_button_confirm_new_yes_clicked(self, widget):
        self.dialog_confirm_new.hide()
        self.changed = False
        self.filename = None
        self.fg.new()
        self.update_function_list()
        self.graph_update()

    def on_button_confirm_new_cancel_clicked(self, widget):
        self.dialog_confirm_new.hide()

    def on_dialog_confirm_new_delete_event(self, widget, event):
        self.dialog_confirm_new.hide()
        return True

    def on_button_fileopen_open_clicked(self, widget):
        filename = self.fcdialog_open.get_filename()
        folder = self.fcdialog_open.get_current_folder()
        logging.debug('Loading file: '+filename)
        try:
            filehandler = open(filename, "rb")
            try:
                self.fg = pickle.load(filehandler)
                filehandler.close()
                self.folder = folder
                self.fg.update_xylimits()
                self.update_function_list()
                self.graph_update()
                self.fcdialog_open.hide()
                self.changed = False
                self.filename = filename
            except:
                self.label_open_error.\
                    set_text(\
                    _("File doesn't look like a FunctionPlot file."))
                self.dialog_file_open_error.show()
        except:
            self.label_open_error.set_text(_('Error reading file.'))
            self.dialog_file_open_error.show()
    
    def on_button_fileopen_cancel_clicked(self, widget):
        self.fcdialog_open.hide()

    def on_filechooserdialog_open_delete_event(self, widget, event):
        self.fcdialog_open.hide()
        return True

    def on_button_file_open_error_close_clicked(self, widget):
        self.dialog_file_open_error.hide()

    def on_dialog_file_open_error_delete_event(self, widget, event):
        self.dialog_file_open_error.hide()
        return True

    def on_button_filesave_save_clicked(self, widget):
        filename = self.fcdialog_save.get_filename()
        try:
            if os.path.isdir(filename):
                self.fcdialog_save.set_current_folder(filename)
                self.folder = filename
            else:
                if not filename.lower().endswith('.functionplot'):
                    filename = filename+'.functionplot'
                folder = self.fcdialog_save.get_current_folder()
                self.filename = filename
                self.folder = folder
                if os.path.isfile(filename):
                    logging.debug('File already exists: '+filename)
                    self.dialog_overwrite.show()
                else:
                    saved = self._save()
        # TypeError is raised if the filename is empty, or only
        # spaces, or has invalid characters.
        except TypeError:
            pass

    def on_button_filesave_cancel_clicked(self, widget):
        self.fcdialog_save.hide()

    def on_filechooserdialog_save_delete_event(self, widget, event):
        self.fcdialog_save.hide()
        return True
    
    def on_button_save_error_close_clicked(self, widget):
        self.dialog_file_save_error.hide()

    def on_dialog_file_save_error_delete_event(self, widget, event):
        self.dialog_file_save_error.hide()
        return True

    def on_button_overwrite_yes_clicked(self, widget):
        self.dialog_overwrite.hide()
        self._save()

    def on_button_overwrite_cancel_clicked(self, widget):
        self.dialog_overwrite.hide()
        self.fcdialog_save.hide()

    def on_button_overwrite_no_clicked(self, widget):
        self.dialog_overwrite.hide()

    def on_dialog_overwrite_delete_event(self, widget, event):
        self.dialog_overwrite.hide()
        return True

    def on_button_confirm_open_yes_clicked(self, widget):
        self.fcdialog_open.set_current_folder(self.folder)
        self.dialog_confirm_open.hide()
        self.fcdialog_open.show()

    def on_button_confirm_open_cancel_clicked(self, widget):
        self.dialog_confirm_open.hide()

    def on_dialog_confirm_open_delete_event(self, widget, event):
        self.dialog_confirm_open.hide()
        return True

    def on_button_export_yes_clicked(self, widget):
        filename = self.fcdialog_export.get_filename()
        try:
            if os.path.isdir(filename):
                self.fcdialog_export.set_current_folder(filename)
                self.folder = filename
            else:
                if not filename.lower().endswith('.png'):
                    filename = filename+'.png'
                self.export_filename = filename
                folder = self.fcdialog_export.get_current_folder()
                self.folder = folder
                if os.path.isfile(filename):
                    logging.debug('File already exists: '+filename)
                    self.dialog_export_overwrite.show()
                else:
                    saved = self._export()
        # TypeError is raised if the filename is empty, or only
        # spaces, or has invalid characters.
        except TypeError:
            pass


    def on_button_export_cancel_clicked(self, widget):
        self.fcdialog_export.hide()

    def on_filechooserdialog_export_delete_event(self, widget,
            event):
        self.fcdialog_export.hide()
        return True

    def on_button_export_overwrite_yes_clicked(self, widget):
        self.dialog_export_overwrite.hide()
        self._export()

    def on_button_export_overwrite_cancel_clicked(self, widget):
        self.dialog_export_overwrite.hide()
        self.fcdialog_export.hide()

    def on_button_export_overwrite_no_clicked(self, widget):
        self.dialog_export_overwrite.hide()

    def on_dialog_export_overwrite_delete_event(self, widget, event):
        self.dialog_export_overwrite.hide()
        return True

    def on_button_export_error_close_clicked(self, widget):
        self.dialog_file_export_error.hide()

    def on_dialog_file_export_error_delete_event(self, widget,
            event):
        self.dialog_file_export_error.hide()
        return True

    # save the graph
    def _save(self):
        try:
            filehandler = open(self.filename, "wb")
            pickle.dump(self.fg, filehandler)
            filehandler.close()
            logging.debug('File saved: '+self.filename)
            self.changed = False
            self.fcdialog_save.hide()
            return True
        except:
            self.dialog_file_save_error.show()
            return False

    # export the graph to png
    def _export(self):
        try:
            filename = self.export_filename
            self.fig.savefig(filename, dpi=300)
            self.fcdialog_export.hide()
        except:
            self.dialog_file_export_error.show()

    def __init__(self):
        # Only a few colors defined. Hard to find more that will
        # stand out. If there are more functions, colors will cycle
        # from the start.
        # colors were taken mostly from http://latexcolor.com/
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
        # filenames to save to/open from and export to
        self.filename = None
        self.export_filename = None
        # create a FunctionGraph object
        self.fg = FunctionGraph()
        # we need this to keep track if the file has changed since
        # last save
        self.changed = False 
        # we'll need this for panning
        self.mousebutton_press = None
        
        # Load GUI from glade file
        builder = gtk.Builder()
        builder.add_from_file('functionplot.glade')
        
        #
        # Main Window
        #
        self.window = builder.get_object('functionplot')
        # Adjust window size to 80% of working area
        try:
            w = gtk.gdk.get_default_root_window()
            p = gtk.gdk.atom_intern('_NET_WORKAREA')
            workarea_width, workarea_height = w.property_get(p)[2][2:4]
            width = int(workarea_width*0.8)
            height = int(workarea_height*0.8)
        except TypeError:
            width = 700
            height= 500
        self.window.set_default_size(width, height)
        #self.window.maximize()
        # menus
        self.imagemenuitem_quit = \
            builder.get_object('imagemenuitem_quit')
        
        self.checkmenuitem_function_intersections = \
            builder.get_object('checkmenuitem_function_intersections')
        self.checkmenuitem_function_intersections.\
                set_active(self.fg.point_type_enabled[1])
        self.checkmenuitem_x_intercepts = \
            builder.get_object('checkmenuitem_x_intercepts')
        self.checkmenuitem_x_intercepts.\
                set_active(self.fg.point_type_enabled[2])
        self.checkmenuitem_y_intercepts = \
            builder.get_object('checkmenuitem_y_intercepts')
        self.checkmenuitem_y_intercepts.\
                set_active(self.fg.point_type_enabled[3])
        self.checkmenuitem_extrema = \
            builder.get_object('checkmenuitem_extrema')
        self.checkmenuitem_extrema.\
                set_active(self.fg.point_type_enabled[4])
        self.checkmenuitem_inflection = \
            builder.get_object('checkmenuitem_inflection')
        self.checkmenuitem_inflection.\
                set_active(self.fg.point_type_enabled[5])
        self.checkmenuitem_vertical_asym = \
            builder.get_object('checkmenuitem_vertical_asym')
        self.checkmenuitem_vertical_asym.\
                set_active(self.fg.point_type_enabled[6])
        self.checkmenuitem_horizontal_asym = \
            builder.get_object('checkmenuitem_horizontal_asym')
        self.checkmenuitem_horizontal_asym.\
                set_active(self.fg.point_type_enabled[7])
        self.checkmenuitem_slope45 = \
            builder.get_object('checkmenuitem_slope45')
        self.checkmenuitem_slope45.\
                set_active(self.fg.point_type_enabled[8])
        self.checkmenuitem_outliers = \
            builder.get_object('checkmenuitem_outliers')
        self.checkmenuitem_outliers.set_active(self.fg.outliers)
        self.checkmenuitem_show_poi = \
            builder.get_object('checkmenuitem_show_poi')
        self.checkmenuitem_show_poi.set_active(self.fg.show_poi)
        self.checkmenuitem_legend = \
            builder.get_object('checkmenuitem_legend')
        self.checkmenuitem_legend.set_active(self.fg.show_legend)
        # main toolbar
        self.btn_auto = builder.get_object('btn_auto')
        self.btn_auto.set_active(self.fg.auto)

        # graph in main window
        self.table = builder.get_object('table_graph')
        self.fig = Figure(facecolor='w', tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.table.attach(self.canvas, 0, 1, 0, 1)
        # function list
        self.ls_functions = \
            builder.get_object('liststore_functions')
        self.ls_functions.clear()
        self.treeview_functions = \
            builder.get_object('treeview_functions')
        self.cr_toggle_visible = \
            builder.get_object('cr_toggle_visible')
        # catch mouse wheel scroll
        self.canvas.mpl_connect('scroll_event', self.wheel_zoom)
        # catch click and pan
        self.canvas.mpl_connect('button_press_event',
                self.pan_press)
        self.canvas.mpl_connect('button_release_event',
                self.pan_release)
        self.canvas.mpl_connect('motion_notify_event',
                self.pan_motion)
        self.graph_update()

        #
        # file open/save dialogs
        #
        self.fcdialog_open = \
            builder.get_object('filechooserdialog_open')
        self.fcdialog_save = \
            builder.get_object('filechooserdialog_save')
        filefilter = gtk.FileFilter()
        filefilter.set_name(_('FunctionPlot files'))
        filefilter.add_pattern('*.functionplot')
        filefilter.add_pattern('*.FUNCTIONPLOT')
        self.fcdialog_open.add_filter(filefilter)
        self.fcdialog_save.add_filter(filefilter)
        self.dialog_file_open_error = \
            builder.get_object('dialog_file_open_error')
        self.label_open_error = \
            builder.get_object('label_open_error')
        self.dialog_file_save_error = \
            builder.get_object('dialog_file_save_error')
        self.folder = os.path.expanduser("~")
        # overwrite dialog
        self.dialog_overwrite = \
            builder.get_object('dialog_overwrite')
        self.label_overwrite = builder.get_object('label_overwrite')
        # confirm open dialog
        self.dialog_confirm_open = \
            builder.get_object('dialog_confirm_open')
        # confirm new dialog
        self.dialog_confirm_new = \
            builder.get_object('dialog_confirm_new')
        # export dialogs
        self.fcdialog_export = \
            builder.get_object('filechooserdialog_export')
        exportfilter = gtk.FileFilter()
        exportfilter.set_name(_('PNG image files'))
        exportfilter.add_pattern('*.png')
        exportfilter.add_pattern('*.PNG')
        self.fcdialog_export.add_filter(exportfilter)
        self.dialog_export_overwrite = \
            builder.get_object('dialog_export_overwrite')
        self.dialog_file_export_error = \
            builder.get_object('dialog_file_export_error')
        #
        # Add function dialog
        #
        self.dialog_add_function = \
            builder.get_object('dialog_add_function')
        self.entry_function = builder.get_object('entry_function')
        self.dialog_add_error = \
            builder.get_object('dialog_add_error')
        # Calculating... window
        self.window_calculating = \
            builder.get_object('window_calculating')

        # Connect all signals
        builder.connect_signals(self)
        self.window.show_all()



if __name__ == "__main__":
    app = GUI()
    gtk.main()

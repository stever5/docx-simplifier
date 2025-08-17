"""
GUI interface for docx-simplifier using wxPython with progress reporting.

This module provides a graphical interface with file browsing,
level selection, progress reporting, and performance statistics.
"""

import os
import threading
import time
import wx

from .core import DocxSimplifier
from .levels import LEVEL_DESCRIPTIONS, get_level_description
from .utils import format_file_size
from .constants import LARGE_FILE_THRESHOLD, GUI_WINDOW_WIDTH, GUI_WINDOW_HEIGHT


class InfoDialog(wx.Dialog):
    """Dialog showing level descriptions."""
    
    def __init__(self, parent):
        super().__init__(parent, title="Simplification Levels", 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.init_ui()
        self.SetSize(650, 450)
        self.SetMinSize((600, 400))
        self.CenterOnParent()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Simplification Level Descriptions")
        title_font = title.GetFont()
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_font.SetPointSize(title_font.GetPointSize() + 2)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Descriptions
        descriptions_text = []
        for level in sorted(LEVEL_DESCRIPTIONS.keys()):
            descriptions_text.append(f"Level {level}: {LEVEL_DESCRIPTIONS[level]}")
        
        text_ctrl = wx.TextCtrl(panel, value="\n\n".join(descriptions_text),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        vbox.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(close_btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(vbox)
    
    def on_close(self, event):
        """Handle close button."""
        self.EndModal(wx.ID_CLOSE)


class ProgressDialog(wx.ProgressDialog):
    """Enhanced progress dialog with detailed status."""
    
    def __init__(self, parent, title="Processing Document"):
        super().__init__(
            title, 
            "Initializing...",
            maximum=100,
            parent=parent,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME
        )
        self.SetSize(450, 250)
        self.SetMinSize((400, 200))
        self.CenterOnParent()
    
    def update_progress(self, message: str, percentage: float):
        """Update progress with message and percentage."""
        return self.Update(int(percentage), message)


class PerformanceStatsDialog(wx.Dialog):
    """Dialog showing performance statistics and optimization info."""
    
    def __init__(self, parent, stats, processing_time, file_sizes):
        super().__init__(parent, title="Performance Statistics", 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.stats = stats
        self.processing_time = processing_time
        self.file_sizes = file_sizes
        
        self.init_ui()
        self.SetSize(650, 550)
        self.SetMinSize((600, 500))
        self.CenterOnParent()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="🚀 Performance Statistics")
        title_font = title.GetFont()
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_font.SetPointSize(title_font.GetPointSize() + 2)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Stats text
        stats_text = self._format_stats()
        text_ctrl = wx.TextCtrl(panel, value=stats_text,
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        text_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(close_btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(vbox)
    
    def _format_stats(self):
        """Format statistics into readable text."""
        input_size, output_size = self.file_sizes
        file_size_reduction = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
        processing_rate = input_size / self.processing_time if self.processing_time > 0 else 0
        
        # Get XML content reduction
        xml_before = self.stats.get('xml_size_before', 0)
        xml_after = self.stats.get('xml_size_after', 0)
        xml_reduction = self.stats.get('xml_reduction_percent', 0)
        
        xml_section = ""
        if xml_before > 0:
            xml_section = f"""
📄 XML CONTENT ANALYSIS
XML Before:  {self._format_size(xml_before)}
XML After:   {self._format_size(xml_after)}
XML Reduction: {xml_reduction:.1f}%
"""
        
        return f"""⏱️  PROCESSING PERFORMANCE
Processing Time: {self.processing_time:.2f} seconds
Processing Rate: {self._format_size(processing_rate)}/second

📁 FILE SIZE ANALYSIS
Input Size:  {self._format_size(input_size)}
Output Size: {self._format_size(output_size)}
File Reduction: {file_size_reduction:.1f}%{xml_section}
🔧 PROCESSING DETAILS
Approach: {self.stats.get('approach', 'LXML')}
Elements Removed: {self.stats.get('elements_removed', 'N/A'):,}
Elements Modified: {self.stats.get('elements_modified', 'N/A'):,}
Total Time: {self.stats.get('total_time', 'N/A')}

🚀 APPLIED OPTIMIZATIONS
{chr(10).join(f"• {opt}" for opt in self.stats.get('optimizations', []))}"""
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format."""
        return format_file_size(size_bytes)
    
    def on_close(self, event):
        """Handle close button."""
        self.EndModal(wx.ID_CLOSE)


class MainFrame(wx.Frame):
    """Main application window with optimized processing."""
    
    def __init__(self):
        super().__init__(None, title="DOCX Simplifier", size=(GUI_WINDOW_WIDTH, GUI_WINDOW_HEIGHT))
        
        self.simplifier = None
        self.input_file = ""
        self.processing_thread = None
        self.progress_dialog = None
        
        # Set minimum size to prevent layout issues
        self.SetMinSize((650, 550))
        
        self.init_ui()
        self.init_menu()
        self.Center()
    
    def init_menu(self):
        """Initialize the menu bar."""
        menubar = wx.MenuBar()
        
        # Help menu
        help_menu = wx.Menu()
        info_item = help_menu.Append(wx.ID_ANY, "&Info\tF1", 
                                    "Show simplification level descriptions")
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About DOCX Simplifier")
        
        # Performance menu
        perf_menu = wx.Menu()
        stats_item = perf_menu.Append(wx.ID_ANY, "&Statistics", 
                                     "Show performance statistics (after processing)")
        
        menubar.Append(help_menu, "&Help")
        menubar.Append(perf_menu, "&Performance")
        self.SetMenuBar(menubar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_info, info_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_show_stats, stats_item)
        
        # Store for later access
        self.stats_menu_item = stats_item
        self.stats_menu_item.Enable(False)  # Disabled until processing completes
    
    def init_ui(self):
        """Initialize the main UI."""
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="DOCX Simplifier")
        title_font = title.GetFont()
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_font.SetPointSize(title_font.GetPointSize() + 4)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # File selection
        file_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Input File")
        
        file_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_text = wx.TextCtrl(panel, style=wx.TE_READONLY)
        browse_btn = wx.Button(panel, label="Browse...")
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        
        file_hbox.Add(self.file_text, 1, wx.ALL | wx.EXPAND, 5)
        file_hbox.Add(browse_btn, 0, wx.ALL, 5)
        file_box.Add(file_hbox, 0, wx.ALL | wx.EXPAND, 5)
        
        # File info
        self.file_info = wx.StaticText(panel, label="")
        file_box.Add(self.file_info, 0, wx.ALL, 5)
        
        vbox.Add(file_box, 0, wx.ALL | wx.EXPAND, 8)
        
        # Level selection
        level_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Simplification Level")
        
        level_hbox = wx.BoxSizer(wx.HORIZONTAL)
        level_hbox.Add(wx.StaticText(panel, label="0"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.level_slider = wx.Slider(panel, value=1, minValue=0, maxValue=8, 
                                    style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.level_slider.Bind(wx.EVT_SLIDER, self.on_level_change)
        level_hbox.Add(self.level_slider, 1, wx.ALL | wx.EXPAND, 5)
        
        level_hbox.Add(wx.StaticText(panel, label="8"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        level_box.Add(level_hbox, 0, wx.ALL | wx.EXPAND, 5)
        
        # Level description
        self.level_desc = wx.StaticText(panel, label=get_level_description(1))
        self.level_desc.Wrap(600)  # Increased wrap width
        level_box.Add(self.level_desc, 0, wx.ALL | wx.EXPAND, 5)  # No expansion
        
        vbox.Add(level_box, 0, wx.ALL | wx.EXPAND, 8)  # No expansion
        
        # Options
        options_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Options")
        
        self.progress_cb = wx.CheckBox(panel, label="Show progress dialog (recommended for large files)")
        self.progress_cb.SetValue(True)
        options_box.Add(self.progress_cb, 0, wx.ALL, 5)
        
        vbox.Add(options_box, 0, wx.ALL | wx.EXPAND, 8)
        
        # Buttons
        btn_hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_hbox.AddStretchSpacer()
        
        self.process_btn = wx.Button(panel, label="Process")
        self.process_btn.Bind(wx.EVT_BUTTON, self.on_process)
        self.process_btn.Enable(False)
        btn_hbox.Add(self.process_btn, 0, wx.ALL, 5)
        
        vbox.Add(btn_hbox, 0, wx.ALL | wx.EXPAND, 5)
        
        # Status bar
        self.status_text = wx.StaticText(panel, label="Ready - Select a DOCX file to begin")
        vbox.Add(self.status_text, 0, wx.ALL | wx.EXPAND, 5)
        
        panel.SetSizer(vbox)
        
        # Ensure proper layout
        panel.SetAutoLayout(True)
        self.Layout()
        
        # Resize window to fit content exactly
        panel.Fit()
        self.Fit()
        
        # Store processing stats for later display
        self.last_stats = None
        self.last_processing_time = 0
        self.last_file_sizes = (0, 0)
    
    def on_browse(self, event):
        """Handle browse button click."""
        with wx.FileDialog(self, "Choose DOCX file",
                          wildcard="DOCX files (*.docx)|*.docx|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            
            if dlg.ShowModal() == wx.ID_OK:
                self.input_file = dlg.GetPath()
                self.file_text.SetValue(self.input_file)
                
                # Show file info
                try:
                    file_size = os.path.getsize(self.input_file)
                    size_str = self._format_file_size(file_size)
                    
                    if file_size > LARGE_FILE_THRESHOLD:
                        info_text = f"Size: {size_str} (Large file - progress dialog recommended)"
                        self.file_info.SetForegroundColour(wx.Colour(200, 100, 0))
                    else:
                        info_text = f"Size: {size_str}"
                        self.file_info.SetForegroundColour(wx.Colour(0, 0, 0))
                    
                    self.file_info.SetLabel(info_text)
                except:
                    self.file_info.SetLabel("Could not read file size")
                
                self.process_btn.Enable(True)
                self.status_text.SetLabel("File selected - Ready to process")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        return format_file_size(size_bytes)
    
    def on_level_change(self, event):
        """Handle level slider change."""
        level = self.level_slider.GetValue()
        self.level_desc.SetLabel(get_level_description(level))
        self.level_desc.Wrap(500)
        self.Layout()
    
    def on_info(self, event):
        """Show info dialog."""
        with InfoDialog(self) as dlg:
            dlg.ShowModal()
    
    def on_about(self, event):
        """Show about dialog."""
        try:
            info = wx.adv.AboutDialogInfo()
            info.SetName("DOCX Simplifier")
            info.SetVersion("1.0.0")
            info.SetDescription("High-performance DOCX file structure simplifier\nLXML-based processing with guaranteed XML validity")
            info.SetCopyright("(C) 2025")
            info.SetLicence("GPL-3.0")
            wx.adv.AboutBox(info)
        except AttributeError:
            # Fallback for older wxPython versions
            wx.MessageBox(
                "DOCX Simplifier v1.0.0\n\n"
                "High-performance DOCX file structure simplifier\n"
                "LXML-based processing with guaranteed XML validity\n\n"
                "(C) 2025\n"
                "License: GPL-3.0",
                "About DOCX Simplifier",
                wx.OK | wx.ICON_INFORMATION
            )
    
    def on_show_stats(self, event):
        """Show performance statistics dialog."""
        if self.last_stats:
            with PerformanceStatsDialog(self, self.last_stats, 
                                      self.last_processing_time, 
                                      self.last_file_sizes) as dlg:
                dlg.ShowModal()
        else:
            wx.MessageBox("No statistics available. Process a file first.", 
                         "No Statistics", wx.OK | wx.ICON_INFORMATION)
    
    def on_process(self, event):
        """Handle process button click."""
        if not self.input_file:
            wx.MessageBox("Please select an input file first.", "Error", 
                         wx.OK | wx.ICON_ERROR)
            return
        
        # Disable UI during processing
        self.process_btn.Enable(False)
        self.status_text.SetLabel("Processing...")
        
        # Set up progress dialog if requested
        progress_cb = None
        if self.progress_cb.GetValue():
            self.progress_dialog = ProgressDialog(self, "Processing DOCX File")
            progress_cb = self._progress_callback
        
        # Run processing in separate thread
        self.processing_thread = threading.Thread(
            target=self.process_file, 
            args=(progress_cb,)
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def _progress_callback(self, message: str, percentage: float):
        """Progress callback for the processing thread."""
        if self.progress_dialog:
            wx.CallAfter(self._update_progress_dialog, message, percentage)
    
    def _update_progress_dialog(self, message: str, percentage: float):
        """Update progress dialog on main thread."""
        if self.progress_dialog:
            should_continue, _ = self.progress_dialog.update_progress(message, percentage)
            if not should_continue:
                # User cancelled
                self.progress_dialog.Destroy()
                self.progress_dialog = None
                self.processing_complete_error("Processing cancelled by user")
    
    def process_file(self, progress_callback):
        """Process the file in a separate thread."""
        try:
            level = self.level_slider.GetValue()
            
            # Get input file size
            input_size = os.path.getsize(self.input_file)
            
            # Create simplifier
            self.simplifier = DocxSimplifier(
                progress_callback=progress_callback
            )
            
            # Record start time
            start_time = time.time()
            
            # Process the file
            output_path = self.simplifier.simplify_file(
                input_path=self.input_file,
                level=level
            )
            
            # Record end time and get stats
            end_time = time.time()
            processing_time = end_time - start_time
            output_size = os.path.getsize(output_path)
            stats = self.simplifier.get_performance_stats()
            
            # Store stats for later viewing
            self.last_stats = stats
            self.last_processing_time = processing_time
            self.last_file_sizes = (input_size, output_size)
            
            # Update UI on main thread
            wx.CallAfter(self.processing_complete, output_path, level, processing_time, input_size, output_size)
            
        except Exception as e:
            wx.CallAfter(self.processing_complete_error, str(e))
    
    def processing_complete(self, output_path, level, processing_time, input_size, output_size):
        """Handle successful processing completion."""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.Destroy()
            self.progress_dialog = None
        
        self.process_btn.Enable(True)
        
        # Calculate size reduction
        size_reduction = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
        
        self.status_text.SetLabel(f"Complete: {os.path.basename(output_path)} ({processing_time:.1f}s)")
        
        # Enable stats menu
        self.stats_menu_item.Enable(True)
        
        message = (f"✅ Successfully simplified file!\n\n"
                  f"Output: {output_path}\n"
                  f"Level: {level} - {get_level_description(level)}\n\n"
                  f"⏱️ Processing time: {processing_time:.2f} seconds\n"
                  f"📁 Size reduction: {size_reduction:.1f}%\n\n"
                  f"💡 View detailed performance statistics in the Performance menu.")
        
        wx.MessageBox(message, "Processing Complete", wx.OK | wx.ICON_INFORMATION)
    
    def processing_complete_error(self, error_msg):
        """Handle processing error."""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.Destroy()
            self.progress_dialog = None
        
        self.process_btn.Enable(True)
        self.status_text.SetLabel("Error occurred")
        
        wx.MessageBox(f"❌ Error processing file:\n{error_msg}", "Processing Error", 
                     wx.OK | wx.ICON_ERROR)


class DocxSimplifierApp(wx.App):
    """Main application class."""
    
    def OnInit(self):
        """Initialize the application."""
        frame = MainFrame()
        frame.Show()
        return True


def main():
    """Main GUI entry point."""
    app = DocxSimplifierApp()
    app.MainLoop()


if __name__ == '__main__':
    main()

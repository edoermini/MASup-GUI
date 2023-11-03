import sys
from PyQt5.QtWidgets import QMenu, QSplitter, QLabel, QActionGroup, QStatusBar, QToolBar, QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QAction, QTableWidgetItem
from PyQt5.QtCore import Qt
import qtawesome as qta
import qdarktheme

from gui.tables.responsive_table_widget import ResponsiveTableWidget
from gui.updaters import ProgressTableUpdater
from gui.dialogs import ReadProcessMemory
from gui.flowcharts import GraphvizZoomableFlowchart

from analysis import Analysis
from analysis import Workflow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.workflow = Workflow()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("MASup (Malware Analysis Supporter)")

        # Creare un widget a pila per le diverse viste
        stacked_widget = QStackedWidget()

        splitter = QSplitter(Qt.Vertical)
        
        progress_page = QWidget()
        progress_page_layout = QVBoxLayout(progress_page)
        progress_page_layout.addWidget(QLabel("Analysis process"))
        self.progress_table = ResponsiveTableWidget(1, ['Name', 'Phase', 'Status'])
        progress_page_layout.addWidget(self.progress_table)

        suggestions_splitter = QSplitter(Qt.Horizontal)

        progress_suggestions_page = QWidget()
        progress_suggestions_page_layout = QVBoxLayout(progress_suggestions_page)
        progress_suggestions_page_layout.addWidget(QLabel("Progress suggestions"))
        progress_suggestions_page_layout.addWidget(ResponsiveTableWidget(1, ['Name', 'Phase', 'Tools']))

        tools_suggestions_page = QWidget()
        tools_suggestions_page_layout = QVBoxLayout(tools_suggestions_page)
        tools_suggestions_page_layout.addWidget(QLabel("Tools suggestions"))
        tools_suggestions_page_layout.addWidget(ResponsiveTableWidget(1, ['Tool', 'Nature', 'Desciption', 'Run']))

        suggestions_splitter.addWidget(progress_suggestions_page)
        suggestions_splitter.addWidget(tools_suggestions_page)

        splitter.addWidget(progress_page)
        splitter.addWidget(suggestions_splitter)

        stacked_widget.addWidget(splitter)

        workflow_view = GraphvizZoomableFlowchart(self.workflow.dot_code())

        workflow_page = QWidget()
        workflow_page_layout = QVBoxLayout(workflow_page)
        workflow_page_layout.addWidget(workflow_view)
        stacked_widget.addWidget(workflow_page)

        self.setCentralWidget(stacked_widget)

        self.toolbar = QToolBar("Toolbar", self)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        toolbar_actions = QActionGroup(self)
        toolbar_actions.setExclusive(True)

        progress_button = QAction(qta.icon("fa5s.tasks"), "Progress", self)
        progress_button.setStatusTip("Analysis' progresses")
        progress_button.triggered.connect(lambda: stacked_widget.setCurrentIndex(0))
        progress_button.setCheckable(True)
        progress_button.setChecked(True)
        toolbar_actions.addAction(progress_button)
        self.toolbar.addAction(progress_button)

        suggestions_button = QAction(qta.icon('fa5s.stream'), "Flow", self)
        suggestions_button.setStatusTip("Analysis' suggestions")
        suggestions_button.triggered.connect(lambda: stacked_widget.setCurrentIndex(1))
        suggestions_button.setCheckable(True)
        toolbar_actions.addAction(suggestions_button)
        self.toolbar.addAction(suggestions_button)

        self.toolbar.addSeparator()

        self.setStatusBar(QStatusBar(self))

        # Aggiungere il menu "File" con un'opzione di uscita
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        exit_action = QAction('Quit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Aggiungere un menu "View" con una checkbox
        view_menu = menubar.addMenu('View')

        show_toolbar_action = QAction('Show toolbar', self, checkable=True)
        show_toolbar_action.setChecked(True)
        show_toolbar_action.triggered.connect(self.toolbar.setVisible)
        view_menu.addAction(show_toolbar_action)

        appearance_submenu = QMenu('Appearance', self)
        dark_mode_action = QAction('Dark mode', self, checkable=True)
        dark_mode_action.setChecked(False)
        dark_mode_action.triggered.connect(lambda checked : qdarktheme.setup_theme('dark' if checked else 'light'))
        appearance_submenu.addAction(dark_mode_action)

        view_menu.addMenu(appearance_submenu)

        analysis_menu = menubar.addMenu('Analysis')
        process_injection_menu = QMenu('Process injection', self)
        extract_injected_action = QAction('Read process memory', self, checkable=False)
        extract_injected_action.triggered.connect(lambda: ReadProcessMemory(self).exec_())
        process_injection_menu.addAction(extract_injected_action)

        analysis_menu.addMenu(process_injection_menu)

        layout = QVBoxLayout()
        layout.addWidget(stacked_widget)

        # Creare un widget principale e impostare il layout principale
        main_widget = QWidget()
        main_widget.setLayout(layout)

        # Impostare il widget principale come widget centrale della finestra principale
        self.setCentralWidget(main_widget)

        self.analysis = Analysis(self.workflow)

        self.process_table_updater = ProgressTableUpdater(self)
        self.process_table_updater.start()
    
    def update_progress_table(self):
        self.analysis.update_activities()

        for row, (_, activity) in enumerate(self.analysis.activities.items()):
            
            if row == self.progress_table.rowCount():
                self.progress_table.insertRow(row)

            columns = [activity["name"], activity["phase"], "active" if activity["active"] else "ended"]

            for col, value in enumerate(columns):
                item = QTableWidgetItem(value)
                #item.setData(Qt.EditRole, value)
                self.progress_table.setItem(row, col, item)

    def closeEvent(self, event):
        self.process_table_updater.stop()
        self.process_table_updater.join()
        event.accept()
    
    def close(self) -> bool:
        self.tmp_dir.cleanup()
        return super().close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qdarktheme.setup_theme('light')

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

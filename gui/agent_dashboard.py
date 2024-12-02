import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import pandas as pd
import random
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now import dotenv
from dotenv import load_dotenv

print("Loading environment variables...")
# Load environment variables
load_dotenv()
print("Environment variables loaded.")

from src.agent import Agent
from src.specialized_agents import ResearchAgent, AnalyticsAgent, CoordinatorAgent
from src.paper_agent import PaperAgent, ResearchPaper
from src.llm_manager import LLMManager

print("Imports completed successfully.")

class MARCDashboard:
    def __init__(self, master):
        self.master = master
        master.title("MARC - Multi-Agent Research Collaborator")
        master.geometry("1200x800")
        master.configure(bg='#f0f0f0')

        # Initialize LLM Manager
        self.llm_manager = LLMManager()
        print("LLM Manager initialized.")

        # Create agents
        self.coordinator = CoordinatorAgent()
        self.research_agent = ResearchAgent(research_domain="AI")
        self.analytics_agent = AnalyticsAgent()
        self.paper_agent = PaperAgent()
        print("Agents created.")

        # Register agents
        self.coordinator.register_agent(self.research_agent)
        self.coordinator.register_agent(self.analytics_agent)
        self.coordinator.register_agent(self.paper_agent)
        print("Agents registered.")

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create LLM Selection Tab
        self.create_llm_selection_tab()

        # Create other tabs (initially disabled)
        self.create_research_tab()
        self.create_paper_library_tab()
        self.create_agent_network_tab()
        self.create_collaboration_log_tab()
        self.create_research_paper_tab(self.notebook)

        # Disable tabs until LLM is selected
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")

    def create_llm_selection_tab(self):
        # LLM Selection Tab
        llm_frame = ttk.Frame(self.notebook)
        self.notebook.add(llm_frame, text="LLM Selection")

        # Title
        title_label = tk.Label(llm_frame, text="Select Large Language Model", 
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=20)

        # Available LLMs
        available_llms = self.llm_manager.get_available_llms()

        # LLM Selection Buttons
        button_frame = tk.Frame(llm_frame)
        button_frame.pack(pady=20)

        for llm_name, llm_details in available_llms.items():
            llm_button = tk.Button(
                button_frame, 
                text=f"{llm_name}\n{llm_details['provider']} - {llm_details['model']}", 
                command=lambda name=llm_name: self.select_llm(name),
                width=30,
                height=3
            )
            llm_button.pack(pady=10)

        # Status Label
        self.llm_status_label = tk.Label(llm_frame, 
                                         text="Please select an LLM to activate agents", 
                                         font=('Helvetica', 12))
        self.llm_status_label.pack(pady=20)

    def select_llm(self, llm_name):
        """
        Select an LLM and activate agents
        """
        try:
            # Select LLM
            llm_config = self.llm_manager.select_llm(llm_name)
            
            if not llm_config:
                messagebox.showerror("LLM Selection Error", f"Could not select {llm_name}")
                return
            
            # Update status
            self.llm_status_label.config(
                text=f"Selected LLM: {llm_name}\n"
                     f"Provider: {llm_config['provider']}\n"
                     f"Model: {llm_config['model']}",
                fg='green'
            )
            
            # Enable other tabs
            for i in range(1, self.notebook.index("end")):
                self.notebook.tab(i, state="normal")
            
            # Switch to Research Tab
            self.notebook.select(1)
            
            # Log collaboration
            self.log_collaboration(f"LLM Selected: {llm_name}")
            
            messagebox.showinfo("LLM Activated", 
                                f"{llm_name} LLM activated. All agents are now ready!")
        
        except Exception as e:
            messagebox.showerror("LLM Selection Error", str(e))

    def create_research_tab(self):
        research_frame = ttk.Frame(self.notebook)
        self.notebook.add(research_frame, text="Research")

        # Create main container with paned window
        paned = ttk.PanedWindow(research_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel for filters and controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Filters section
        filters_frame = ttk.LabelFrame(left_frame, text="Research Filters")
        filters_frame.pack(fill=tk.X, padx=5, pady=5)

        # Date range filter
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(date_frame, text="Date Range:").pack(side=tk.LEFT)
        self.date_from = ttk.Entry(date_frame, width=10)
        self.date_from.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="to").pack(side=tk.LEFT)
        self.date_to = ttk.Entry(date_frame, width=10)
        self.date_to.pack(side=tk.LEFT, padx=5)

        # Topic filter
        topic_frame = ttk.Frame(filters_frame)
        topic_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(topic_frame, text="Topics:").pack(side=tk.LEFT)
        self.topic_var = tk.StringVar(value="All")
        topics = ["All", "Machine Learning", "Natural Language Processing", "Multi-Agent Systems", "Robotics"]
        topic_menu = ttk.OptionMenu(topic_frame, self.topic_var, "All", *topics)
        topic_menu.pack(side=tk.LEFT, padx=5)

        # Citation count filter
        citation_frame = ttk.Frame(filters_frame)
        citation_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(citation_frame, text="Min Citations:").pack(side=tk.LEFT)
        self.min_citations = ttk.Entry(citation_frame, width=10)
        self.min_citations.pack(side=tk.LEFT, padx=5)

        # Apply filters button
        apply_btn = ttk.Button(filters_frame, text="Apply Filters", command=self.apply_research_filters)
        apply_btn.pack(pady=10)

        # Visualization options
        viz_frame = ttk.LabelFrame(left_frame, text="Visualization")
        viz_frame.pack(fill=tk.X, padx=5, pady=5)

        # Chart type selector
        chart_frame = ttk.Frame(viz_frame)
        chart_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(chart_frame, text="Chart Type:").pack(side=tk.LEFT)
        self.chart_type = tk.StringVar(value="bar")
        charts = ["bar", "line", "scatter", "pie"]
        chart_menu = ttk.OptionMenu(chart_frame, self.chart_type, "bar", *charts,
                                   command=self.update_research_visualization)
        chart_menu.pack(side=tk.LEFT, padx=5)

        # Right panel for results and visualization
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # Results section
        results_frame = ttk.LabelFrame(right_frame, text="Research Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tree view for results
        columns = ("Title", "Authors", "Date", "Citations", "Topics")
        self.research_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        for col in columns:
            self.research_tree.heading(col, text=col)
            self.research_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.research_tree.yview)
        self.research_tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.research_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Visualization section
        viz_container = ttk.LabelFrame(right_frame, text="Research Trends")
        viz_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create matplotlib figure for visualization
        self.research_fig, self.research_ax = plt.subplots(figsize=(8, 4))
        self.research_canvas = FigureCanvasTkAgg(self.research_fig, master=viz_container)
        self.research_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize with some sample data
        self.load_sample_research_data()

    def apply_research_filters(self):
        try:
            # Get filter values
            date_from = self.date_from.get()
            date_to = self.date_to.get()
            topic = self.topic_var.get()
            min_citations = self.min_citations.get()

            # Clear existing items
            for item in self.research_tree.get_children():
                self.research_tree.delete(item)

            # Apply filters to data (this is a placeholder - implement actual filtering)
            filtered_data = self.filter_research_data(date_from, date_to, topic, min_citations)

            # Update tree view
            for item in filtered_data:
                self.research_tree.insert("", tk.END, values=item)

            # Update visualization
            self.update_research_visualization()

        except Exception as e:
            messagebox.showerror("Error", f"Error applying filters: {str(e)}")

    def update_research_visualization(self, *args):
        try:
            self.research_ax.clear()
            chart_type = self.chart_type.get()

            # Get data from tree view
            data = []
            for item in self.research_tree.get_children():
                values = self.research_tree.item(item)["values"]
                data.append(values)

            if not data:
                return

            # Convert to pandas DataFrame for easier manipulation
            df = pd.DataFrame(data, columns=["Title", "Authors", "Date", "Citations", "Topics"])

            if chart_type == "bar":
                # Citations by topic
                topic_citations = df.groupby("Topics")["Citations"].sum()
                topic_citations.plot(kind="bar", ax=self.research_ax)
                self.research_ax.set_title("Citations by Topic")
                self.research_ax.set_xlabel("Topics")
                self.research_ax.set_ylabel("Total Citations")

            elif chart_type == "line":
                # Citations over time
                df["Date"] = pd.to_datetime(df["Date"])
                time_series = df.groupby("Date")["Citations"].sum()
                time_series.plot(kind="line", ax=self.research_ax)
                self.research_ax.set_title("Citations Over Time")
                self.research_ax.set_xlabel("Date")
                self.research_ax.set_ylabel("Citations")

            elif chart_type == "scatter":
                # Citations vs. Date
                df["Date"] = pd.to_datetime(df["Date"])
                self.research_ax.scatter(df["Date"], df["Citations"])
                self.research_ax.set_title("Citations vs. Date")
                self.research_ax.set_xlabel("Date")
                self.research_ax.set_ylabel("Citations")

            elif chart_type == "pie":
                # Distribution of papers by topic
                topic_counts = df["Topics"].value_counts()
                topic_counts.plot(kind="pie", ax=self.research_ax, autopct="%1.1f%%")
                self.research_ax.set_title("Distribution of Papers by Topic")

            self.research_ax.tick_params(axis='x', rotation=45)
            self.research_fig.tight_layout()
            self.research_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Error updating visualization: {str(e)}")

    def load_sample_research_data(self):
        # Sample data for demonstration
        sample_data = [
            ("Deep Learning in Multi-Agent Systems", "Smith, J., Jones, K.", "2023-01-15", 150, "Machine Learning"),
            ("Natural Language Processing for Agent Communication", "Brown, M.", "2023-02-20", 75, "Natural Language Processing"),
            ("Cooperative Robot Learning", "Wilson, R., Taylor, S.", "2023-03-10", 120, "Robotics"),
            ("Multi-Agent Reinforcement Learning", "Davis, A.", "2023-04-05", 200, "Multi-Agent Systems"),
        ]

        for item in sample_data:
            self.research_tree.insert("", tk.END, values=item)

        self.update_research_visualization()

    def filter_research_data(self, date_from, date_to, topic, min_citations):
        # This is a placeholder - implement actual filtering logic
        # For now, return sample data
        return [
            ("Deep Learning in Multi-Agent Systems", "Smith, J., Jones, K.", "2023-01-15", 150, "Machine Learning"),
            ("Natural Language Processing for Agent Communication", "Brown, M.", "2023-02-20", 75, "Natural Language Processing"),
        ]

    def create_paper_library_tab(self):
        # Paper Library Tab
        paper_frame = ttk.Frame(self.notebook)
        self.notebook.add(paper_frame, text="Paper Library")

        # Create main container with paned window
        paned = ttk.PanedWindow(paper_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel for paper management
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Add Paper Section
        add_paper_frame = ttk.LabelFrame(left_frame, text="Add New Paper")
        add_paper_frame.pack(fill=tk.X, padx=5, pady=5)

        # Paper Details Inputs
        details_frame = ttk.Frame(add_paper_frame)
        details_frame.pack(padx=5, pady=5, fill=tk.X)

        # Title
        ttk.Label(details_frame, text="Title:").pack(fill=tk.X)
        self.paper_title_entry = ttk.Entry(details_frame)
        self.paper_title_entry.pack(fill=tk.X, pady=2)

        # Authors
        ttk.Label(details_frame, text="Authors (comma-separated):").pack(fill=tk.X)
        self.paper_authors_entry = ttk.Entry(details_frame)
        self.paper_authors_entry.pack(fill=tk.X, pady=2)

        # Abstract
        ttk.Label(details_frame, text="Abstract:").pack(fill=tk.X)
        self.paper_abstract = scrolledtext.ScrolledText(details_frame, height=4)
        self.paper_abstract.pack(fill=tk.X, pady=2)

        # URL
        ttk.Label(details_frame, text="Paper URL:").pack(fill=tk.X)
        self.paper_url_entry = ttk.Entry(details_frame)
        self.paper_url_entry.pack(fill=tk.X, pady=2)

        # Topics (Multiple selection)
        ttk.Label(details_frame, text="Topics:").pack(fill=tk.X)
        self.topics_frame = ttk.Frame(details_frame)
        self.topics_frame.pack(fill=tk.X, pady=2)
        self.topic_vars = {}
        topics = ["Machine Learning", "NLP", "Multi-Agent Systems", "Robotics", "AI"]
        for i, topic in enumerate(topics):
            var = tk.BooleanVar()
            self.topic_vars[topic] = var
            ttk.Checkbutton(self.topics_frame, text=topic, variable=var).grid(row=i//3, column=i%3, padx=5)

        # Add Paper Button
        add_paper_button = ttk.Button(add_paper_frame, text="Add Paper", command=self.add_paper_to_library)
        add_paper_button.pack(pady=5)

        # Import/Export Section
        import_export_frame = ttk.LabelFrame(left_frame, text="Import/Export")
        import_export_frame.pack(fill=tk.X, padx=5, pady=5)

        # Import buttons
        import_bibtex_btn = ttk.Button(import_export_frame, text="Import BibTeX", command=self.import_bibtex)
        import_bibtex_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        import_doi_btn = ttk.Button(import_export_frame, text="Import from DOI", command=self.import_from_doi)
        import_doi_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Export buttons
        export_bibtex_btn = ttk.Button(import_export_frame, text="Export BibTeX", command=self.export_bibtex)
        export_bibtex_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Right panel for library display and search
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # Search and Filter Section
        search_frame = ttk.LabelFrame(right_frame, text="Search and Filter")
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        # Search bar with type selector
        search_type_frame = ttk.Frame(search_frame)
        search_type_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_type = tk.StringVar(value="title")
        ttk.Radiobutton(search_type_frame, text="Title", variable=self.search_type, value="title").pack(side=tk.LEFT)
        ttk.Radiobutton(search_type_frame, text="Author", variable=self.search_type, value="author").pack(side=tk.LEFT)
        ttk.Radiobutton(search_type_frame, text="Topic", variable=self.search_type, value="topic").pack(side=tk.LEFT)

        # Search entry
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_entry = ttk.Entry(search_entry_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_btn = ttk.Button(search_entry_frame, text="Search", command=self.search_papers)
        search_btn.pack(side=tk.LEFT, padx=5)

        # Library Display
        library_frame = ttk.LabelFrame(right_frame, text="Paper Library")
        library_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tree view with more columns
        columns = ("Title", "Authors", "Topics", "Added Date", "Citations")
        self.paper_library_tree = ttk.Treeview(library_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.paper_library_tree.heading(col, text=col, command=lambda c=col: self.sort_library(c))
            self.paper_library_tree.column(col, width=100)

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(library_frame, orient=tk.VERTICAL, command=self.paper_library_tree.yview)
        x_scrollbar = ttk.Scrollbar(library_frame, orient=tk.HORIZONTAL, command=self.paper_library_tree.xview)
        self.paper_library_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # Pack tree and scrollbars
        self.paper_library_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind double-click event for paper details
        self.paper_library_tree.bind("<Double-1>", self.show_paper_details)

        # Context menu
        self.create_library_context_menu()

        # Load sample data
        self.load_sample_library_data()

    def create_library_context_menu(self):
        self.library_menu = tk.Menu(self.master, tearoff=0)
        self.library_menu.add_command(label="View Details", command=self.view_selected_paper)
        self.library_menu.add_command(label="Open URL", command=self.open_paper_url)
        self.library_menu.add_command(label="Copy Citation", command=self.copy_citation)
        self.library_menu.add_separator()
        self.library_menu.add_command(label="Edit", command=self.edit_paper)
        self.library_menu.add_command(label="Delete", command=self.delete_paper)

        self.paper_library_tree.bind("<Button-3>", self.show_library_menu)

    def show_library_menu(self, event):
        try:
            item = self.paper_library_tree.identify_row(event.y)
            if item:
                self.paper_library_tree.selection_set(item)
                self.library_menu.post(event.x_root, event.y_root)
        finally:
            self.library_menu.grab_release()

    def view_selected_paper(self):
        selected = self.paper_library_tree.selection()
        if selected:
            self.show_paper_details(None)

    def open_paper_url(self):
        selected = self.paper_library_tree.selection()
        if selected:
            # Implement URL opening logic
            pass

    def copy_citation(self):
        selected = self.paper_library_tree.selection()
        if selected:
            # Get paper details and create citation
            values = self.paper_library_tree.item(selected[0])["values"]
            citation = f"{values[1]} ({values[3]}). {values[0]}."
            self.master.clipboard_clear()
            self.master.clipboard_append(citation)
            messagebox.showinfo("Success", "Citation copied to clipboard!")

    def edit_paper(self):
        selected = self.paper_library_tree.selection()
        if selected:
            # Implement edit logic
            pass

    def delete_paper(self):
        selected = self.paper_library_tree.selection()
        if selected and messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this paper?"):
            self.paper_library_tree.delete(selected)

    def sort_library(self, column):
        # Get all items
        items = [(self.paper_library_tree.set(item, column), item) for item in self.paper_library_tree.get_children("")]
        
        # Sort items
        items.sort(reverse=hasattr(self, "sort_reverse") and self.sort_reverse)
        
        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.paper_library_tree.move(item, "", index)
        
        # Reverse sort next time
        self.sort_reverse = not getattr(self, "sort_reverse", False)

    def import_bibtex(self):
        file_path = filedialog.askopenfilename(
            title="Select BibTeX File",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]
        )
        if file_path:
            # Implement BibTeX import logic
            messagebox.showinfo("Success", "BibTeX file imported successfully!")

    def import_from_doi(self):
        doi = simpledialog.askstring("Import from DOI", "Enter DOI:")
        if doi:
            # Implement DOI import logic
            messagebox.showinfo("Success", "Paper imported from DOI successfully!")

    def export_bibtex(self):
        file_path = filedialog.asksaveasfilename(
            title="Export BibTeX",
            defaultextension=".bib",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]
        )
        if file_path:
            # Implement BibTeX export logic
            messagebox.showinfo("Success", "Library exported to BibTeX successfully!")

    def load_sample_library_data(self):
        sample_data = [
            ("Deep Learning in Multi-Agent Systems", "Smith, J., Jones, K.", "ML, AI", "2023-01-15", 150),
            ("Natural Language Processing for Agents", "Brown, M.", "NLP, AI", "2023-02-20", 75),
            ("Cooperative Robot Learning", "Wilson, R., Taylor, S.", "Robotics, AI", "2023-03-10", 120),
            ("Multi-Agent Reinforcement Learning", "Davis, A.", "ML, AI", "2023-04-05", 200),
        ]

        for item in sample_data:
            self.paper_library_tree.insert("", tk.END, values=item)

    def create_agent_network_tab(self):
        # Agent Network Visualization Tab
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="Agent Network")

        # Create top control panel
        control_panel = ttk.Frame(network_frame)
        control_panel.pack(fill=tk.X, padx=10, pady=5)

        # Add refresh button
        refresh_btn = ttk.Button(control_panel, text="Refresh Network", command=self.refresh_network)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Add layout options
        layout_label = ttk.Label(control_panel, text="Layout:")
        layout_label.pack(side=tk.LEFT, padx=5)
        self.layout_var = tk.StringVar(value="spring")
        layouts = ["spring", "circular", "random", "shell"]
        layout_menu = ttk.OptionMenu(control_panel, self.layout_var, "spring", *layouts, 
                                    command=self.update_network_layout)
        layout_menu.pack(side=tk.LEFT, padx=5)

        # Add agent status frame
        status_frame = ttk.LabelFrame(network_frame, text="Agent Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create status indicators for each agent
        self.status_indicators = {}
        for agent in [self.coordinator, self.research_agent, self.analytics_agent, self.paper_agent]:
            agent_frame = ttk.Frame(status_frame)
            agent_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Agent name and role
            ttk.Label(agent_frame, text=f"{agent.name} ({agent.role}):").pack(side=tk.LEFT)
            
            # Status indicator (green=active, red=inactive)
            status_indicator = ttk.Label(agent_frame, text="●", foreground="green")
            status_indicator.pack(side=tk.LEFT, padx=5)
            self.status_indicators[agent.name] = status_indicator

            # Last activity timestamp
            timestamp_label = ttk.Label(agent_frame, text="Last active: Now")
            timestamp_label.pack(side=tk.LEFT, padx=5)

        # Create NetworkX graph
        self.G = nx.DiGraph()
        
        # Create matplotlib figure
        plt.close('all')
        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor='#f0f0f0')
        
        # Create canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=network_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Add interaction log
        log_frame = ttk.LabelFrame(network_frame, text="Agent Interactions")
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.interaction_log = scrolledtext.ScrolledText(log_frame, height=5)
        self.interaction_log.pack(fill=tk.X, padx=5, pady=5)

        # Initialize the network
        self.refresh_network()
        
        # Start periodic updates
        self.update_agent_statuses()

    def refresh_network(self):
        self.ax.clear()
        
        # Add agents as nodes
        agents = [self.coordinator, self.research_agent, self.analytics_agent, self.paper_agent]
        for agent in agents:
            self.G.add_node(agent.name, role=agent.role)
        
        # Add interactions as edges
        self.G.add_edge(self.coordinator.name, self.research_agent.name)
        self.G.add_edge(self.coordinator.name, self.analytics_agent.name)
        self.G.add_edge(self.research_agent.name, self.paper_agent.name)

        # Get the selected layout
        layout_type = self.layout_var.get()
        if layout_type == "spring":
            pos = nx.spring_layout(self.G)
        elif layout_type == "circular":
            pos = nx.circular_layout(self.G)
        elif layout_type == "random":
            pos = nx.random_layout(self.G)
        else:
            pos = nx.shell_layout(self.G)

        # Draw the network
        node_colors = ['lightblue', 'lightgreen', 'lightsalmon', 'lightpink']
        nx.draw(self.G, pos,
                with_labels=True,
                node_color=node_colors[:len(self.G.nodes)],
                node_size=2000,
                font_size=10,
                font_weight='bold',
                ax=self.ax,
                edge_color='gray')

        # Add role labels
        role_labels = nx.get_node_attributes(self.G, 'role')
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] + 0.08)
        
        nx.draw_networkx_labels(self.G, pos_attrs,
                              labels={n: f"Role: {r}" for n, r in role_labels.items()},
                              font_size=8,
                              font_color='darkblue')

        self.ax.set_title("Multi-Agent System Interaction Network", fontweight='bold')
        self.ax.set_facecolor('#f0f0f0')
        self.canvas.draw()

    def update_network_layout(self, *args):
        self.refresh_network()

    def update_agent_statuses(self):
        # This would normally check actual agent status
        # For demo, we'll just toggle between active/inactive randomly
        for agent_name, indicator in self.status_indicators.items():
            is_active = random.choice([True, False])
            indicator.configure(foreground="green" if is_active else "red")
            
            # Log interaction if status changed
            if is_active:
                self.log_interaction(f"{agent_name} became active")
        
        # Schedule next update
        self.master.after(5000, self.update_agent_statuses)

    def log_interaction(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.interaction_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.interaction_log.see(tk.END)

    def create_collaboration_log_tab(self):
        # Collaboration Log Tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Collaboration Log")

        # Collaboration Log Display
        self.collaboration_log = scrolledtext.ScrolledText(log_frame, 
                                                           wrap=tk.WORD, 
                                                           width=80, 
                                                           height=20)
        self.collaboration_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Log Action Buttons
        button_frame = tk.Frame(log_frame)
        button_frame.pack(pady=10)

        clear_log_button = tk.Button(button_frame, text="Clear Log", 
                                     command=self.clear_collaboration_log)
        clear_log_button.pack()

    def create_research_paper_tab(self, notebook):
        """
        Create a tab for research paper collection and display
        """
        research_papers_frame = ttk.Frame(notebook)
        notebook.add(research_papers_frame, text="Research Papers")

        # Search Frame
        search_frame = ttk.Frame(research_papers_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Search Entry with Label
        search_label = ttk.Label(search_frame, text="Enter search query:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = ttk.Entry(search_frame, width=50)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: search_papers())

        # Progress Bar
        self.search_progress = ttk.Progressbar(research_papers_frame, mode='indeterminate')
        self.search_progress.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))
        self.search_progress.pack_forget()  # Hide initially

        # Status Label
        self.status_label = ttk.Label(research_papers_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.TOP, padx=10, pady=(0, 5))

        # Treeview for displaying papers
        self.research_papers_tree = ttk.Treeview(research_papers_frame, columns=("Title", "Authors", "Source", "URL"), show="headings")
        self.research_papers_tree.heading("Title", text="Title")
        self.research_papers_tree.heading("Authors", text="Authors")
        self.research_papers_tree.heading("Source", text="Source")
        self.research_papers_tree.heading("URL", text="URL")
        
        # Configure column widths
        self.research_papers_tree.column("Title", width=300)
        self.research_papers_tree.column("Authors", width=200)
        self.research_papers_tree.column("Source", width=100)
        self.research_papers_tree.column("URL", width=200)
        
        self.research_papers_tree.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(research_papers_frame, orient=tk.VERTICAL, command=self.research_papers_tree.yview)
        self.research_papers_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def search_papers():
            try:
                query = search_entry.get().strip()
                if not query:
                    self.status_label.config(text="Please enter a search query.", foreground="red")
                    return

                # Clear previous results
                for i in self.research_papers_tree.get_children():
                    self.research_papers_tree.delete(i)

                # Show progress bar and update status
                self.search_progress.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))
                self.search_progress.start(10)
                self.status_label.config(text="Searching papers...", foreground="gray")
                self.master.update()

                # Search papers
                papers = self.paper_agent.search_papers(query)

                # Hide progress bar
                self.search_progress.stop()
                self.search_progress.pack_forget()

                if papers:
                    # Update treeview with results
                    for paper in papers:
                        self.research_papers_tree.insert("", tk.END, values=(
                            paper.title,
                            ", ".join(paper.authors),
                            paper.source,
                            paper.url
                        ))
                    self.status_label.config(
                        text=f"Found {len(papers)} papers from multiple sources.",
                        foreground="green"
                    )
                else:
                    self.status_label.config(
                        text="No papers found. Try a different search query.",
                        foreground="orange"
                    )
            except Exception as e:
                self.search_progress.stop()
                self.search_progress.pack_forget()
                self.status_label.config(
                    text=f"Error searching papers: {str(e)}",
                    foreground="red"
                )

        # Buttons Frame
        buttons_frame = ttk.Frame(research_papers_frame)
        buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Search Button
        search_button = ttk.Button(
            buttons_frame,
            text="Search Papers",
            command=search_papers
        )
        search_button.pack(side=tk.LEFT, padx=(0, 5))

        # Export Button
        export_button = ttk.Button(
            buttons_frame,
            text="Export Results",
            command=self.export_research_papers
        )
        export_button.pack(side=tk.LEFT, padx=5)

        # Open Link Button
        open_link_button = ttk.Button(
            buttons_frame,
            text="Open Paper Link",
            command=self.open_selected_paper_link
        )
        open_link_button.pack(side=tk.LEFT, padx=5)

        # Paper Details Window
        def show_paper_details(event):
            selected_item = self.research_papers_tree.selection()
            if selected_item:
                # Create a new window to show paper details
                details_window = tk.Toplevel(self.master)
                details_window.title("Paper Details")
                details_window.geometry("800x600")
                details_window.minsize(600, 400)

                # Get the selected paper details
                item_values = self.research_papers_tree.item(selected_item[0])['values']
                
                # Create a text widget to display details
                details_text = scrolledtext.ScrolledText(
                    details_window,
                    wrap=tk.WORD,
                    width=80,
                    height=30,
                    font=('TkDefaultFont', 10)
                )
                details_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
                
                # Format and insert details
                details_text.insert(tk.END, f"Title:\n{item_values[0]}\n\n")
                details_text.insert(tk.END, f"Authors:\n{item_values[1]}\n\n")
                details_text.insert(tk.END, f"Source:\n{item_values[2]}\n\n")
                details_text.insert(tk.END, f"URL:\n{item_values[3]}\n\n")
                
                # Add a "Open in Browser" button
                open_button = ttk.Button(
                    details_window,
                    text="Open in Browser",
                    command=lambda: webbrowser.open(item_values[3]) if item_values[3] else None
                )
                open_button.pack(side=tk.BOTTOM, pady=10)
                
                # Make the text read-only
                details_text.config(state=tk.DISABLED)

        self.research_papers_tree.bind('<Double-1>', show_paper_details)

        return research_papers_frame

    def perform_research(self):
        try:
            topic = self.topic_entry.get() or "Large Language Model Multi-Agent Systems"
            research_findings = self.research_agent.conduct_research(topic)
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Display research findings
            self.results_text.insert(tk.END, "Research Findings:\n")
            self.results_text.insert(tk.END, f"Topic: {topic}\n")
            self.results_text.insert(tk.END, f"Domain: {research_findings.get('domain', 'N/A')}\n")
            self.results_text.insert(tk.END, "Key Findings:\n")
            for finding in research_findings.get('key_findings', []):
                self.results_text.insert(tk.END, f"- {finding}\n")
            
            # Update collaboration log
            self.log_collaboration(f"Research conducted on topic: {topic}")
            
            messagebox.showinfo("Research Complete", "Research task completed successfully!")
        
        except Exception as e:
            messagebox.showerror("Research Error", str(e))

    def analyze_findings(self):
        try:
            # Get the current research findings from the text
            research_text = self.results_text.get(1.0, tk.END).strip()
            
            if not research_text:
                messagebox.showwarning("Warning", "Conduct research first!")
                return
            
            # Simulate data for analysis
            analysis_data = {
                "topic": self.topic_entry.get(),
                "research_text": research_text
            }
            
            # Perform analysis
            analysis_result = self.analytics_agent.analyze_data(analysis_data)
            
            # Display analysis results
            self.results_text.insert(tk.END, "\n\nAnalysis Results:\n")
            for insight in analysis_result.get('insights', []):
                self.results_text.insert(tk.END, f"- {insight}\n")
            
            self.results_text.insert(tk.END, f"\nRecommendation: {analysis_result.get('recommendation', 'No specific recommendation')}")
            
            # Update collaboration log
            self.log_collaboration("Analysis of research findings completed")
            
            messagebox.showinfo("Analysis Complete", "Data analysis completed successfully!")
        
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

    def add_paper_to_library(self):
        try:
            # Gather paper details
            title = self.paper_title_entry.get().strip()
            authors = [a.strip() for a in self.paper_authors_entry.get().split(',')]
            
            if not title or not authors:
                messagebox.showwarning("Invalid Input", "Please enter title and authors")
                return
            
            # Create ResearchPaper object
            paper = ResearchPaper(
                title=title,
                authors=authors,
                research_domains=["AI", "Multi-Agent Systems"]
            )
            
            # Add paper to library
            paper_id = self.paper_agent.add_paper(paper)
            
            # Update treeview
            self.paper_library_tree.insert('', 'end', 
                values=(paper.title, ', '.join(paper.authors), paper.publication_date))
            
            # Clear input fields
            self.paper_title_entry.delete(0, tk.END)
            self.paper_authors_entry.delete(0, tk.END)
            
            # Update collaboration log
            self.log_collaboration(f"Added paper: {title}")
            
            messagebox.showinfo("Success", "Paper added to library")
        
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_papers(self):
        try:
            # Get search keyword
            keyword = self.search_entry.get().strip()
            
            if not keyword:
                messagebox.showwarning("Invalid Search", "Please enter a search keyword")
                return
            
            # Search papers
            results = self.paper_agent.search_papers(keyword)

            # Clear existing treeview
            for i in self.paper_library_tree.get_children():
                self.paper_library_tree.delete(i)
            
            # Populate treeview with results
            for paper in results:
                self.paper_library_tree.insert('', 'end', 
                    values=(paper.title, ', '.join(paper.authors), paper.publication_date))
            
            # Update collaboration log
            self.log_collaboration(f"Searched papers with keyword: {keyword}")
            
            messagebox.showinfo("Search Complete", f"Found {len(results)} papers")
        
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def log_collaboration(self, message):
        """
        Log collaboration activities
        """
        # Add timestamp to message
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        # Insert message into collaboration log
        if hasattr(self, 'collaboration_log'):
            self.collaboration_log.insert(tk.END, full_message)
            self.collaboration_log.see(tk.END)

    def clear_collaboration_log(self):
        """
        Clear the collaboration log
        """
        self.collaboration_log.delete(1.0, tk.END)
        self.log_collaboration("Collaboration log cleared")

    def export_research_papers(self):
        """
        Export collected research papers to a CSV file
        """
        try:
            # Get the current collected papers from the PaperAgent
            papers = self.paper_agent.collected_papers
            
            if not papers:
                messagebox.showinfo("Export Papers", "No papers to export.")
                return
            
            # Open a file dialog to choose export location
            export_filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialdir=os.path.join(project_root, 'exports')
            )
            
            if export_filename:
                # Export papers to the chosen file
                exported_file = self.paper_agent.export_papers_to_csv(
                    papers=papers, 
                    filename=os.path.basename(export_filename)
                )
                
                if exported_file:
                    messagebox.showinfo(
                        "Export Successful", 
                        f"Papers exported to:\n{exported_file}"
                    )
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def open_selected_paper_link(self):
        """
        Open the web link of the selected research paper
        """
        try:
            # Get the selected item from the research papers treeview
            selected_item = self.research_papers_tree.selection()
            
            if not selected_item:
                messagebox.showinfo("Open Link", "Please select a paper first.")
                return
            
            # Retrieve the paper details
            item_values = self.research_papers_tree.item(selected_item[0])['values']
            
            # Assuming the URL is the last column in the treeview
            paper_url = item_values[-1]
            
            if paper_url and paper_url.startswith(('http://', 'https://')):
                import webbrowser
                webbrowser.open(paper_url)
            else:
                messagebox.showinfo("Open Link", "No valid URL found for this paper.")
        except Exception as e:
            messagebox.showerror("Open Link Error", str(e))

    def show_paper_details(self, event):
        """Display detailed information about the selected paper in a new window."""
        # Get the selected item
        selected_item = self.paper_library_tree.selection()
        if not selected_item:
            return

        # Get paper details from the selected item
        item = selected_item[0]
        values = self.paper_library_tree.item(item)['values']
        if not values:
            return

        # Create a new window for paper details
        details_window = tk.Toplevel(self.master)
        details_window.title("Paper Details")
        details_window.geometry("600x400")

        # Create a frame with padding
        frame = ttk.Frame(details_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Add paper details
        ttk.Label(frame, text="Title:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text=values[0], wraplength=550).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame, text="Authors:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text=values[1], wraplength=550).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame, text="Abstract:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        abstract_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=8)
        abstract_text.insert(tk.END, values[2])
        abstract_text.configure(state='disabled')
        abstract_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(frame, text="URL:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        url_text = ttk.Label(frame, text=values[3], wraplength=550, foreground="blue", cursor="hand2")
        url_text.pack(anchor=tk.W, pady=(0, 10))
        url_text.bind("<Button-1>", lambda e: self.open_paper_url())

        ttk.Label(frame, text="Topics:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text=values[4], wraplength=550).pack(anchor=tk.W, pady=(0, 10))

        # Add a close button
        ttk.Button(frame, text="Close", command=details_window.destroy).pack(pady=10)

def run_gui():
    print("Starting GUI...")
    root = tk.Tk()
    dashboard = MARCDashboard(root)
    print("GUI initialized. Starting mainloop...")
    root.mainloop()
    print("GUI mainloop started.")

if __name__ == "__main__":
    print("Running as main script...")
    run_gui()

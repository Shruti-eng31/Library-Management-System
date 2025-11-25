import streamlit as st
import json
from datetime import datetime
from security_utils import ensure_password_fields, hash_password
from program_catalog import all_programmes

__all__ = [
    "admin_login_page",
    "admin_dashboard",
]

def admin_login_page():
    """Admin-only login page"""
    # Header with purple/red gradient - compact
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%); 
                    padding: 0.8rem 0.5rem; border-radius: 8px; margin-bottom: 1rem;
                    box-shadow: 0 2px 8px rgba(108, 3, 69, 0.3);'>
            <h1 style='color: white; text-align: center; font-size: 1.5rem; margin: 0; 
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                🔒 Admin Portal
            </h1>
            <p style='color: #F7C566; text-align: center; font-size: 0.8rem; margin: 0.3rem 0 0 0;
                      text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                Authorized Personnel Only
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style='background: #1e1e1e; padding: 0.8rem; border-radius: 8px; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        border: 1px solid #333333;'>
                <h2 style='color: #ffffff; text-align: center; margin: 0; font-size: 1.1rem;'>
                    🛡️ Administrator Login
                </h2>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

        username = st.text_input(
            "**Admin Username**", placeholder="Enter admin username", key="admin_username"
        )
        password = st.text_input(
            "**Admin Password**",
            type="password",
            placeholder="Enter admin password",
            key="admin_password",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🔐 Admin Login", use_container_width=True, type="primary"):
                if username and password:
                    user = st.session_state.app.verify_login(username, password, "admin")
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = "admin"
                        st.success(f"✅ Welcome, Administrator {user['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid admin credentials! Access denied.")
                else:
                    st.warning("⚠️ Please enter both username and password")

        with col_b:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Security warning
        st.warning(
            "⚠️ **Security Notice:** This area is restricted to authorized administrators only. Unauthorized access attempts are logged."
        )

def admin_dashboard():
    """Admin dashboard with enhanced management features"""
    st.markdown("""
        <div style='background: linear-gradient(135deg, #6C0345 0%, #DC143C 100%); 
                    padding: 0.6rem; border-radius: 8px; margin-bottom: 0.8rem;'>
            <h2 style='color: white; text-align: center; margin: 0; font-size: 1.2rem;'>📊 Admin Dashboard</h2>
            <p style='color: #F7C566; text-align: center; margin: 0.2rem 0 0 0; font-size: 0.75rem;'>
                Complete library management system
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Calculate statistics
    total_books = sum(
        len(books) 
        for program_books in st.session_state.app.books.get('program_books', {}).values()
        for books in [program_books]
    )
    
    total_users = (
        len(st.session_state.app.users.get('students', [])) + 
        len(st.session_state.app.users.get('teachers', []))
    )
    
    active_borrows = len([t for t in st.session_state.app.transactions if t.get('status') == 'borrowed'])
    total_fines = sum(float(t.get('fine', 0)) for t in st.session_state.app.transactions)

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Books", total_books)
    with col2:
        st.metric("👥 Total Users", total_users)
    with col3:
        st.metric("📖 Active Borrows", active_borrows)
    with col4:
        st.metric("💰 Total Fines", f"₹{total_fines:.2f}")

    st.divider()

    # Tabs for different management sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Manage Books", 
        "👥 Manage Users", 
        "📈 Transactions", 
        "⚙️ System"
    ])

    with tab1:
        manage_books_admin()

    with tab2:
        manage_users_admin()

    with tab3:
        view_all_transactions()
        
    with tab4:
        st.markdown("### ⚙️ System Settings")
        if st.button("🔄 Refresh Data", help="Reload all data from storage"):
            st.session_state.app.load_data()
            st.success("Data refreshed successfully!")
            
        if st.button("💾 Backup Data", help="Create a backup of current data"):
            backup_file = f"bookflow_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump({
                    'users': st.session_state.app.users,
                    'books': st.session_state.app.books,
                    'transactions': st.session_state.app.transactions
                }, f, indent=2)
            st.success(f"Backup saved as {backup_file}")

def view_all_transactions():
    """View and manage all book transactions"""
    st.markdown("### 📈 All Transactions")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by status:",
            ["All"] + ["Borrowed", "Returned", "Overdue"],
            key="transaction_status_filter"
        )
    with col2:
        user_filter = st.text_input("Filter by user ID or name:", key="transaction_user_filter")
    with col3:
        book_filter = st.text_input("Filter by book ID or title:", key="transaction_book_filter")
    
    # Get filtered transactions
    transactions = st.session_state.app.transactions
    
    if status_filter != "All":
        if status_filter == "Overdue":
            transactions = [t for t in transactions 
                          if t.get('status') == 'borrowed' 
                          and 'due_date' in t 
                          and t.get('due_date') < datetime.now().strftime('%Y-%m-%d')]
        else:
            transactions = [t for t in transactions if t.get('status') == status_filter.lower()]
    
    if user_filter:
        user_filter = user_filter.lower()
        transactions = [
            t for t in transactions 
            if (user_filter in t.get('user_id', '').lower() or 
                user_filter in t.get('user_name', '').lower())
        ]
    
    if book_filter:
        book_filter = book_filter.lower()
        transactions = [
            t for t in transactions 
            if (book_filter in t.get('book_id', '').lower() or 
                book_filter in t.get('book_title', '').lower())
        ]
    
    # Display transactions
    if transactions:
        st.markdown(f"**Found {len(transactions)} transactions**")
        
        for t in transactions:
            # Determine status color and icon
            if t.get('status') == 'returned':
                status_icon = "✅"
                status_color = "#28a745"
            elif 'due_date' in t and t.get('due_date') < datetime.now().strftime('%Y-%m-%d'):
                status_icon = "⏰"
                status_color = "#dc3545"
            else:
                status_icon = "📅"
                status_color = "#ffc107"
            
            # Calculate days remaining or overdue
            days_info = ""
            if 'due_date' in t and t.get('status') == 'borrowed':
                from datetime import datetime as dt
                due_date = dt.strptime(t['due_date'], '%Y-%m-%d')
                today = dt.today()
                delta = (due_date - today).days
                if delta >= 0:
                    days_info = f" (Due in {delta} days)"
                else:
                    days_info = f" ({abs(delta)} days overdue)"
            
            with st.expander(f"{status_icon} {t.get('book_title', 'Unknown Book')} - {t.get('user_name', 'Unknown User')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        **User:** {t.get('user_name')} ({t.get('user_id')})  
                        **Book:** {t.get('book_title')} ({t.get('book_id')})  
                        **Borrowed on:** {t.get('borrow_date', 'N/A')}  
                        **Due date:** {t.get('due_date', 'N/A')}{days_info}  
                        **Status:** <span style='color: {status_color};'>{t.get('status', 'N/A').title()}</span>  
                        **Fine:** ₹{t.get('fine', 0):.2f}  
                        **Returned on:** {t.get('return_date', 'Not returned yet')}
                    """, unsafe_allow_html=True)
                
                with col2:
                    if t.get('status') == 'borrowed':
                        if st.button("📥 Mark as Returned", key=f"return_{t.get('id')}"):
                            # Find and update the transaction
                            for trans in st.session_state.app.transactions:
                                if trans.get('id') == t.get('id'):
                                    trans['status'] = 'returned'
                                    trans['return_date'] = datetime.now().strftime('%Y-%m-%d')
                                    
                                    # Update book availability
                                    for program, books in st.session_state.app.books.get('program_books', {}).items():
                                        for book in books:
                                            if book.get('id') == t.get('book_id'):
                                                book['available'] = book.get('available', 0) + 1
                                                break
                                    
                                    st.session_state.app.save_data()
                                    st.success("Book marked as returned!")
                                    st.rerun()
                                    break
    else:
        st.info("No transactions found matching the current filters.")

def manage_users_admin():
    """Admin user management with CRUD operations"""
    st.markdown("### 👥 User Management")

    # Add new user form
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("User ID *", help="Unique identifier for the user")
                new_name = st.text_input("Full Name *")
                new_username = st.text_input("Username *")
                new_password = st.text_input("Password *", type="password")
            with col2:
                new_role = st.selectbox("Role *", ["student", "teacher"])
                new_email = st.text_input("Email")
                new_contact = st.text_input("Contact")
                new_program = st.selectbox("Program", [""] + all_programmes(), 
                                         help="Required for students, optional for teachers")
            
            submitted = st.form_submit_button("💾 Add User")
            if submitted:
                if not all([new_id, new_name, new_username, new_password]):
                    st.error("Please fill in all required fields (*)")
                else:
                    # Check for existing user with same ID or username
                    existing = False
                    for role in ['students', 'teachers']:
                        if any(u['id'] == new_id for u in st.session_state.app.users.get(role, [])):
                            st.error(f"A user with ID {new_id} already exists")
                            existing = True
                            break
                        if any(u['username'] == new_username for u in st.session_state.app.users.get(role, [])):
                            st.error(f"Username {new_username} is already taken")
                            existing = True
                            break
                    
                    if not existing:
                        # Hash the password
                        password_hash, password_salt = hash_password(new_password)
                        
                        # Create user object
                        user = {
                            'id': new_id.upper(),
                            'name': new_name,
                            'username': new_username,
                            'password_hash': password_hash,
                            'password_salt': password_salt,
                            'email': new_email if new_email else None,
                            'contact': new_contact if new_contact else None,
                            'programme': new_program if new_program else None
                        }
                        
                        # Add to appropriate user list
                        role_key = 'students' if new_role == 'student' else 'teachers'
                        st.session_state.app.users[role_key].append(user)
                        st.session_state.app.save_data()
                        st.success(f"✅ User {new_name} added successfully!")
                        st.rerun()

    # User list with edit/delete options
    st.markdown("### 👥 User List")
    
    # Filter users by role
    role_filter = st.radio("Filter by role:", ["All"] + list(st.session_state.app.users.keys()), 
                          horizontal=True, key="user_role_filter")
    
    # Get filtered users
    users_to_display = []
    for role, user_list in st.session_state.app.users.items():
        if role_filter == "All" or role == role_filter:
            for user in user_list:
                user_copy = user.copy()
                user_copy['role'] = role
                users_to_display.append(user_copy)
    
    # Search functionality
    search_term = st.text_input("Search users by name, ID, or username")
    if search_term:
        search_term = search_term.lower()
        users_to_display = [
            u for u in users_to_display
            if (search_term in u.get('name', '').lower() or
                search_term in u.get('id', '').lower() or
                search_term in u.get('username', '').lower())
        ]
    
    # Display users
    if users_to_display:
        st.markdown(f"**Found {len(users_to_display)} users**")
        
        for idx, user in enumerate(users_to_display):
            with st.expander(f"👤 {user['name']} ({user['id']})", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        **Role:** {user['role'].title()}  
                        **Username:** {user['username']}  
                        **Email:** {user.get('email', 'N/A')}  
                        **Contact:** {user.get('contact', 'N/A')}  
                        **Program:** {user.get('programme', 'N/A')}
                    """)
                
                with col2:
                    if st.button("✏️ Edit", key=f"user_edit_{idx}_{user['id']}"):
                        st.session_state['editing_user'] = user
                    
                    if st.button("🗑️ Delete", key=f"user_delete_{idx}_{user['id']}"):
                        # Check if user has any active borrows
                        active_borrows = [
                            t for t in st.session_state.app.transactions 
                            if t.get('user_id') == user['id'] and t.get('status') == 'borrowed'
                        ]
                        if active_borrows:
                            st.error("Cannot delete: User has active book borrowings")
                        else:
                            st.session_state.app.users[user['role']] = [
                                u for u in st.session_state.app.users[user['role']] 
                                if u['id'] != user['id']
                            ]
                            st.session_state.app.save_data()
                            st.success("User deleted successfully!")
                            st.rerun()
    else:
        st.info("No users found. Add some users to get started!")

    # Edit user modal
    if 'editing_user' in st.session_state:
        user = st.session_state['editing_user']
        with st.form(f"edit_user_form_{user['id']}"):
            st.markdown(f"### ✏️ Edit User: {user['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=user.get('name', ''))
                new_username = st.text_input("Username", value=user.get('username', ''))
                new_password = st.text_input("Password", type="password", 
                                           help="Leave empty to keep current password")
            with col2:
                new_email = st.text_input("Email", value=user.get('email', ''))
                new_contact = st.text_input("Contact", value=user.get('contact', ''))
                new_program = st.selectbox("Program", 
                                         [""] + all_programmes(),
                                         index=all_programmes().index(user.get('programme', '')) + 1 
                                         if user.get('programme') in all_programmes() else 0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    # Find and update the user
                    for role, users in st.session_state.app.users.items():
                        for u in users:
                            if u['id'] == user['id']:
                                u.update({
                                    'name': new_name,
                                    'username': new_username,
                                    'email': new_email if new_email else None,
                                    'contact': new_contact if new_contact else None,
                                    'programme': new_program if new_program else None
                                })
                                
                                # Update password if provided
                                if new_password:
                                    password_hash, password_salt = hash_password(new_password)
                                    u['password_hash'] = password_hash
                                    u['password_salt'] = password_salt
                                
                                st.session_state.app.save_data()
                                st.success("User updated successfully!")
                                del st.session_state['editing_user']
                                st.rerun()
                                break
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state['editing_user']
                    st.rerun()

def manage_books_admin():
    """Enhanced book management with CRUD operations"""
    st.markdown("### 📚 Book Management")
    
    # Add new book form
    with st.expander("➕ Add New Book", expanded=False):
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            with col1:
                book_id = st.text_input("Book ID *", help="Unique identifier for the book")
                title = st.text_input("Title *")
                author = st.text_input("Author *")
                isbn = st.text_input("ISBN")
            with col2:
                category = st.selectbox("Category *", ["Textbook", "Reference", "Fiction", "Non-Fiction", "Other"])
                copies = st.number_input("Copies *", min_value=1, value=1)
                program = st.selectbox("Program", [""] + all_programmes(), 
                                     help="Leave empty for general books")
            
            description = st.text_area("Description")
            
            submitted = st.form_submit_button("💾 Add Book")
            if submitted:
                if not all([book_id, title, author, category]):
                    st.error("Please fill in all required fields (*)")
                else:
                    new_book = {
                        'id': book_id.upper(),
                        'title': title,
                        'author': author,
                        'category': category,
                        'copies': copies,
                        'available': copies,
                        'isbn': isbn if isbn else None,
                        'description': description if description else None,
                        'programme': program if program else None
                    }
                    
                    # Add to appropriate book list
                    program_key = program if program else 'general'
                    if 'program_books' not in st.session_state.app.books:
                        st.session_state.app.books['program_books'] = {}
                    if program_key not in st.session_state.app.books['program_books']:
                        st.session_state.app.books['program_books'][program_key] = []
                    
                    st.session_state.app.books['program_books'][program_key].append(new_book)
                    st.session_state.app.save_data()
                    st.success("✅ Book added successfully!")
                    st.rerun()

    # Book search and filter
    st.markdown("### 🔍 Search Books")
    search_term = st.text_input("Search by title, author, or ID")
    
    # Get all books
    all_books = []
    for program, books in st.session_state.app.books.get('program_books', {}).items():
        for book in books:
            book_copy = book.copy()
            book_copy['program'] = program if program != 'general' else 'General'
            all_books.append(book_copy)
    
    # Apply search filter
    if search_term:
        search_term = search_term.lower()
        filtered_books = [
            b for b in all_books
            if (search_term in b.get('title', '').lower() or
                search_term in b.get('author', '').lower() or
                search_term in b.get('id', '').lower())
        ]
    else:
        filtered_books = all_books

    # Display books in a table with actions
    if filtered_books:
        st.markdown(f"**Found {len(filtered_books)} books**")
        
        for idx, book in enumerate(filtered_books):
            with st.expander(f"📖 {book['title']} by {book['author']} ({book['id']})", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        **ID:** {book['id']}  
                        **Author:** {book['author']}  
                        **Category:** {book.get('category', 'N/A')}  
                        **Program:** {book.get('program', 'General')}  
                        **Copies:** {book.get('copies', 1)} (Available: {book.get('available', book.get('copies', 1))})  
                        **ISBN:** {book.get('isbn', 'N/A')}  
                        **Description:** {book.get('description', 'No description')}
                    """)
                
                with col2:
                    # Create unique keys using index to prevent duplicates
                    if st.button("✏️ Edit", key=f"book_edit_{idx}_{book['id']}"):
                        st.session_state['editing_book'] = book
                    
                    if st.button("🗑️ Delete", key=f"book_delete_{idx}_{book['id']}"):
                        # Check if any copies are borrowed
                        borrowed = any(
                            t['book_id'] == book['id'] and t['status'] == 'borrowed'
                            for t in st.session_state.app.transactions
                        )
                        if borrowed:
                            st.error("Cannot delete: Some copies are currently borrowed")
                        else:
                            program = book.get('program', 'general')
                            st.session_state.app.books['program_books'][program] = [
                                b for b in st.session_state.app.books['program_books'][program]
                                if b['id'] != book['id']
                            ]
                            st.session_state.app.save_data()
                            st.success("Book deleted successfully!")
                            st.rerun()
    else:
        st.info("No books found. Add some books to get started!")

    # Edit book modal
    if 'editing_book' in st.session_state:
        book = st.session_state['editing_book']
        with st.form(f"edit_book_form_{book['id']}"):
            st.markdown(f"### ✏️ Edit Book: {book['title']}")
            
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("Title", value=book.get('title', ''))
                new_author = st.text_input("Author", value=book.get('author', ''))
                new_category = st.text_input("Category", value=book.get('category', ''))
            with col2:
                new_copies = st.number_input("Total Copies", min_value=1, 
                                           value=book.get('copies', 1))
                new_available = st.number_input("Available Copies", min_value=0, 
                                              max_value=new_copies,
                                              value=book.get('available', book.get('copies', 1)))
                new_isbn = st.text_input("ISBN", value=book.get('isbn', ''))
            
            new_description = st.text_area("Description", 
                                         value=book.get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes"):
                    # Find and update the book
                    for program, books in st.session_state.app.books.get('program_books', {}).items():
                        for b in books:
                            if b['id'] == book['id']:
                                b.update({
                                    'title': new_title,
                                    'author': new_author,
                                    'category': new_category,
                                    'copies': new_copies,
                                    'available': new_available,
                                    'isbn': new_isbn,
                                    'description': new_description
                                })
                                st.session_state.app.save_data()
                                st.success("Book updated successfully!")
                                del st.session_state['editing_book']
                                st.rerun()
                                break
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state['editing_book']
                    st.rerun()
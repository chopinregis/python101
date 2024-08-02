Certainly! I'll improve and format the CSS stylesheet, incorporating industry-standard designs and best practices for this type of application. Here's an enhanced version of your CSS:

```css
/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f7fa;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Typography */
h1, h2, h3 {
    margin-bottom: 0.5em;
    color: #2c3e50;
}

h1 {
    font-size: 2.5em;
    font-weight: 700;
}

h2 {
    font-size: 2em;
    font-weight: 600;
}

a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #2980b9;
    text-decoration: underline;
}

/* Header */
header {
    background: linear-gradient(135deg, #3498db, #2c3e50);
    color: #fff;
    padding: 1em 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
    text-align: center;
    margin: 0;
}

/* Navigation */
nav {
    background-color: #34495e;
    padding: 0.5em 0;
}

nav ul {
    list-style-type: none;
    display: flex;
    justify-content: center;
}

nav ul li {
    margin: 0 1em;
}

nav ul li a {
    color: #ecf0f1;
    font-weight: 500;
}

/* Forms */
form {
    background: #fff;
    padding: 2em;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2em;
}

form label {
    display: block;
    margin-bottom: 0.5em;
    font-weight: 500;
    color: #2c3e50;
}

form input[type="text"],
form input[type="date"],
form textarea {
    width: 100%;
    padding: 0.8em;
    margin-bottom: 1em;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    font-size: 1em;
    transition: border-color 0.3s ease;
}

form input[type="text"]:focus,
form input[type="date"]:focus,
form textarea:focus {
    border-color: #3498db;
    outline: none;
}

form textarea {
    height: 150px;
    resize: vertical;
}

form input[type="submit"] {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 0.8em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

form input[type="submit"]:hover {
    background: #2980b9;
}

/* Lists */
ul {
    list-style-type: none;
}

ul li {
    background: #fff;
    margin-bottom: 1em;
    padding: 1em;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease;
}

ul li:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Buttons */
button {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 0.8em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

button:hover {
    background: #2980b9;
}

/* Result Section */
#alternatives {
    background: #fff;
    padding: 1.5em;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-top: 1.5em;
}

#alternatives h2 {
    margin-top: 0;
    color: #2c3e50;
}

#alternatives p {
    margin: 0.5em 0;
    font-size: 1em;
    color: #34495e;
}

/* Alerts */
.alert {
    padding: 1em;
    margin-bottom: 1em;
    border: 1px solid transparent;
    border-radius: 4px;
    font-weight: 500;
}

.alert-success {
    color: #155724;
    background-color: #d4edda;
    border-color: #c3e6cb;
}

.alert-error {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        width: 95%;
    }

    form {
        padding: 1.5em;
    }

    nav ul {
        flex-direction: column;
        align-items: center;
    }

    nav ul li {
        margin: 0.5em 0;
    }
}

/* Accessibility */
:focus {
    outline: 3px solid #3498db;
    outline-offset: 2px;
}

/* Print styles */
@media print {
    body {
        font-size: 12pt;
    }

    header, nav, form input[type="submit"], button {
        display: none;
    }

    a {
        text-decoration: underline;
    }
}
```

This improved CSS includes:

1. A more modern color scheme using flat UI colors.
2. Improved typography with better font choices and sizing.
3. Enhanced form styles with focus states and transitions.
4. Responsive design considerations for smaller screens.
5. Accessibility improvements with clear focus states.
6. Print styles for better paper output.
7. Consistent spacing and layout throughout.
8. Subtle animations and transitions for a more engaging user experience.
9. Improved button and interactive element styles.
10. Better structure and comments for maintainability.

To use this CSS:

1. Replace the content of your `static/css/style.css` file with this code.
2. Make sure you're linking to this CSS file in your HTML templates.
3. Consider adding the Roboto font to your HTML head for better typography:

```html
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
```

This CSS provides a clean, modern look that's suitable for a hospital queue system while maintaining readability and usability. It also includes some best practices for web design, such as responsive layouts and accessibility considerations.
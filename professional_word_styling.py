with open('templates/results.html', 'r') as f:
    content = f.read()

# Remove the old timing-icon styling
import re
content = re.sub(r'\.timing-icon \{[^}]*\}', '', content, flags=re.DOTALL)

# Add new professional word styling that matches your app's design
professional_word_css = '''
        .timing-icon {
            font-size: 0.75rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            padding: 8px 16px;
            border-radius: 25px;
            text-align: center;
            letter-spacing: 1px;
            margin-bottom: 16px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
            text-transform: uppercase;
            min-width: 80px;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .timing-icon:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
        }
        
        /* Special styling for different card types */
        .timing-normal .timing-icon {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
        }
        
        .timing-normal .timing-icon:hover {
            box-shadow: 0 6px 16px rgba(108, 117, 125, 0.4);
        }
        
        /* Ensure consistent spacing */
        .timing-content {
            padding-top: 8px;
        }
        
        .timing-content h4 {
            margin: 8px 0 12px 0;
            font-size: 1.1rem;
            font-weight: 800;
            color: #212529;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .timing-message {
            font-size: 0.95rem;
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .timing-action, .timing-tip, .timing-advice {
            font-size: 0.85rem;
            color: #6c757d;
            margin-bottom: 0;
            font-style: italic;
            line-height: 1.3;
        }
        
        /* Platform timing styling */
        .platform-timing {
            font-size: 0.85rem;
            color: #495057;
            margin: 0 0 8px 0;
            padding: 10px 16px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            border-left: 4px solid #dc3545;
            font-weight: 600;
            backdrop-filter: blur(5px);
        }
        
        /* Summary section styling */
        .timing-summary {
            grid-column: 1 / -1;
            text-align: center;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 28px;
            border-radius: 25px;
            margin-top: 20px;
            box-shadow: 0 8px 24px rgba(220, 53, 69, 0.4);
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .timing-summary h4 {
            margin: 0 0 16px 0;
            font-size: 1.2rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .next-best-time {
            font-size: 1rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.1);
            padding: 12px 24px;
            border-radius: 20px;
            display: inline-block;
            backdrop-filter: blur(10px);
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .timing-icon {
                font-size: 0.7rem;
                padding: 6px 12px;
                min-width: 70px;
            }
            
            .timing-content h4 {
                font-size: 1rem;
            }
            
            .timing-message {
                font-size: 0.9rem;
            }
            
            .timing-action, .timing-tip, .timing-advice {
                font-size: 0.8rem;
            }
        }
'''

# Add the new CSS before closing </style>
content = content.replace('</style>', professional_word_css + '</style>')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Professional word styling applied that matches your app's design!")

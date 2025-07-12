with open('templates/results.html', 'r') as f:
    content = f.read()

# Add timing insights CSS
timing_css = '''
        /* Timing Insights Styles */
        .timing-insights-container {
            padding: 32px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }
        
        .timing-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border-left: 6px solid #6c757d;
            position: relative;
            overflow: hidden;
        }
        
        .timing-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.12);
        }
        
        .timing-optimal {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #d4edda 0%, #ffffff 100%);
        }
        
        .timing-good {
            border-left-color: #ffc107;
            background: linear-gradient(135deg, #fff3cd 0%, #ffffff 100%);
        }
        
        .timing-wait {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da 0%, #ffffff 100%);
        }
        
        .timing-peak {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da 0%, #ffffff 100%);
        }
        
        .timing-high {
            border-left-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da 0%, #ffffff 100%);
        }
        
        .timing-normal {
            border-left-color: #17a2b8;
            background: linear-gradient(135deg, #d1ecf1 0%, #ffffff 100%);
        }
        
        .timing-icon {
            font-size: 2rem;
            margin-bottom: 12px;
            display: inline-block;
        }
        
        .timing-content h4 {
            margin: 0 0 12px 0;
            font-size: 1.2rem;
            font-weight: 700;
            color: #212529;
        }
        
        .timing-message {
            font-size: 1rem;
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
        }
        
        .timing-action, .timing-tip, .timing-advice {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 0;
            font-style: italic;
        }
        
        .platform-timing-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .platform-timing {
            font-size: 0.9rem;
            color: #495057;
            margin: 0;
            padding: 8px 12px;
            background: rgba(255,255,255,0.7);
            border-radius: 10px;
        }
        
        .timing-summary {
            grid-column: 1 / -1;
            text-align: center;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 24px;
            border-radius: 20px;
            margin-top: 16px;
        }
        
        .timing-summary h4 {
            margin: 0 0 12px 0;
            font-size: 1.3rem;
            font-weight: 800;
        }
        
        .next-best-time {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        @media (max-width: 768px) {
            .timing-insights-container {
                grid-template-columns: 1fr;
                padding: 20px;
                gap: 16px;
            }
            
            .timing-card {
                padding: 20px;
            }
            
            .timing-icon {
                font-size: 1.5rem;
            }
        }
'''

# Insert CSS before closing </style>
content = content.replace('</style>', timing_css + '\n        </style>')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Timing insights CSS added!")

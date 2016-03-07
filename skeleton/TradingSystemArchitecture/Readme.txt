All strategies are managed by the PortfolioManager class, and each strategy derives from the StrategyDesign class. 

When a strategy is instanciated, and *added/registered* to the PortfolioManager, the PortfolioManager will connect said strategy to the OrderManagement, to enable said strategy sending orders, through the OrderManagement.send_orders() method.

using System.Windows.Controls;
using System.Windows;
using System.ComponentModel;

namespace PersonalFinanceTracker.WpfApp.Views;

public abstract class BaseViewUserControl : UserControl //, INotifyPropertyChanged
{
    // Register a custom routed event using the Bubble routing strategy.
    public static readonly RoutedEvent ConditionalClickEvent = EventManager.RegisterRoutedEvent(
        name: "ConditionalClick",
        routingStrategy: RoutingStrategy.Bubble,
        handlerType: typeof(RoutedEventHandler),
        ownerType: typeof(UserControl));


    public static readonly RoutedEvent ApplicationStateChangedEvent = EventManager.RegisterRoutedEvent(
        name: "ApplicationStateChanged",
        routingStrategy: RoutingStrategy.Bubble,
        handlerType: typeof(RoutedEventHandler),
        ownerType: typeof(UserControl));

    public event PropertyChangedEventHandler? AuthenticatedStateChanged;
    public event PropertyChangedEventHandler? PropertyChanged;

    // Provide CLR accessors for assigning an event handler.
    //public event RoutedEventHandler ApplicationStateChanged
    //{
    //    add
    //    {
    //        AddHandler(ApplicationStateChangedEvent, value);
    //    }
    //    remove { RemoveHandler(ApplicationStateChangedEvent, value); }
    //}

    //// Provide CLR accessors for assigning an event handler.
    //public event RoutedEventHandler ConditionalClick
    //{
    //    add { 
    //        AddHandler(ConditionalClickEvent, value); 
    //    }
    //    remove { RemoveHandler(ConditionalClickEvent, value); }
    //}

    public void RaiseCustomRoutedEvent()
    {
        // Create a RoutedEventArgs instance.
        RoutedEventArgs routedEventArgs = new(routedEvent: ConditionalClickEvent);

        // Raise the event, which will bubble up through the element tree.
        RaiseEvent(routedEventArgs);
    }

    public void RaiseApplicationStateChangedEvent()
    {
        // Create a RoutedEventArgs instance.
        RoutedEventArgs routedEventArgs = new(routedEvent: ApplicationStateChangedEvent);

        // Raise the event, which will bubble up through the element tree.
        RaiseEvent(routedEventArgs);
    }
}

//public class ApplicationStateChangedMessage
//{
//    public string PropertyC
//}
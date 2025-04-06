using System;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

using Microsoft.Extensions.DependencyInjection;

using PersonalFinanceTracker.WpfApp.Services;
using PersonalFinanceTracker.WpfApp.Views;

namespace PersonalFinanceTracker.WpfApp;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    private readonly IServiceProvider serviceProvider;

    public MainWindow(
        IServiceProvider serviceProvider, 
        IAuthenticationService authenticationService)
    {
        this.serviceProvider = serviceProvider;

        InitializeComponent();
        
        //this.Content = serviceProvider.GetRequiredService<LoginView>();
        //new LoginView(authenticationService);
        MainContentPresenter.Content = serviceProvider.GetRequiredService<LoginView>();

        //MainContentPresenter.AddHandler(AuthenticationService.AuthenticatedStateChangedEvent, new RoutedEventHandler(AuthenticatedStateChanged_Handler));
        authenticationService.AuthenticatedStateChanged += AuthenticationService_PropertyChanged;
    }

    private void AuthenticationService_PropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        MessageBox.Show("TODO: Handler authenticated state changes 2");
        // TODO: If authenticated state is true, load application layout ; else keep login layout
        MainContentPresenter.Content = serviceProvider.GetRequiredService<DefaultLayoutView>();
    }

    //private void MainContentPresenter_ConditionalClick(object sender, RoutedEventArgs e)
    //{
    //    MessageBox.Show("sucess");
    //}

    //private void AuthenticatedStateChanged_Handler(object sender, RoutedEventArgs e)
    //{
    //    MessageBox.Show("TODO: Handler authenticated state changes");
    //}
    
}
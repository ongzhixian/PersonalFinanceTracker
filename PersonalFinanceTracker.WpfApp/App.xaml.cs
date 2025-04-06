using System;
using System.Configuration;
using System.Data;
using System.IO;
using System.Windows;
using System.Windows.Controls;

using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

using PersonalFinanceTracker.WpfApp.Services;
using PersonalFinanceTracker.WpfApp.Views;

namespace PersonalFinanceTracker.WpfApp;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{
    public IServiceProvider ServiceProvider { get; set; }

    public IConfiguration Configuration { get; set; }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        Configuration = GetConfiguration();

        ServiceProvider = GetServiceProvider();

        var mainWindow = ServiceProvider.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    private IServiceProvider GetServiceProvider()
    {
        var services = new ServiceCollection();

        services.AddSingleton<IAuthenticationService, AuthenticationService>();

        services.AddSingleton<MainWindow>();

        services.AddTransient<LoginView>();
        services.AddTransient<DefaultLayoutView>();

        return services.BuildServiceProvider();
    }

    private IConfiguration GetConfiguration()
    {
        var builder = new ConfigurationBuilder();

        builder.SetBasePath(Directory.GetCurrentDirectory());// I'm pretty sure this is the wrong approach;
        builder.AddJsonFile("appsettings.json", true, true);

        return builder.Build();
    }
}


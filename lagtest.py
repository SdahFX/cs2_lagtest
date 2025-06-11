#!/usr/bin/env python3
from pythonping import ping
import statistics
import argparse
import sys
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def color(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m'
    }
    return f"{colors.get(color, '')}{text}\033[0m"

def fetch_cs2_servers(region='eu'):
    """Récupère les serveurs CS2 depuis l'API Steam"""
    region_name = "européens" if region == 'eu' else "américains"
    print(f"🔄 Récupération des serveurs {region_name} depuis l'API Steam...")
    
    try:
        url = "https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        servers = {}
        pops = data.get('pops', {})
        
        if region == 'eu':
            # Codes des régions européennes
            target_regions = [
                'ams',    # Amsterdam
                'fra',    # Frankfurt
                'hel',    # Helsinki
                'lhr',    # London
                'mad',    # Madrid
                'par',    # Paris
                'sto',    # Stockholm
                'vie',    # Vienna
                'waw',    # Warsaw
                'lux',    # Luxembourg
                'mil',    # Milan
                'ath',    # Athens
                'bud',    # Budapest
                'osl',    # Oslo
                'cph',    # Copenhagen
                'prg',    # Prague
                'bru',    # Brussels
                'zrh',    # Zurich
                'rom',    # Rome
                'dub',    # Dublin
                'lis',    # Lisbon
                'bcn',    # Barcelona
            ]
            
            region_names = {
                'ams': 'Amsterdam',
                'fra': 'Frankfurt', 
                'hel': 'Helsinki',
                'lhr': 'London',
                'mad': 'Madrid',
                'par': 'Paris',
                'sto': 'Stockholm',
                'vie': 'Vienna',
                'waw': 'Warsaw',
                'lux': 'Luxembourg',
                'mil': 'Milan',
                'ath': 'Athens',
                'bud': 'Budapest',
                'osl': 'Oslo',
                'cph': 'Copenhagen',
                'prg': 'Prague',
                'bru': 'Brussels',
                'zrh': 'Zurich',
                'rom': 'Rome',
                'dub': 'Dublin',
                'lis': 'Lisbon',
                'bcn': 'Barcelona'
            }
        else:  # region == 'us'
            # Codes des régions américaines
            target_regions = [
                'sea',    # Seattle
                'lax',    # Los Angeles
                'den',    # Denver
                'dfw',    # Dallas
                'ord',    # Chicago
                'iad',    # Washington DC
                'bos',    # Boston
                'atl',    # Atlanta
                'mia',    # Miami
                'phx',    # Phoenix
                'okc',    # Oklahoma City
                'scl',    # Salt Lake City
            ]
            
            region_names = {
                'sea': 'Seattle',
                'lax': 'Los Angeles',
                'den': 'Denver',
                'dfw': 'Dallas',
                'ord': 'Chicago',
                'iad': 'Washington DC',
                'bos': 'Boston',
                'atl': 'Atlanta',
                'mia': 'Miami',
                'phx': 'Phoenix',
                'okc': 'Oklahoma City',
                'scl': 'Salt Lake City'
            }
        
        for pop_code, pop_data in pops.items():
            #print(pop_data)
            if pop_code.lower() in target_regions:
                relay_addresses = pop_data.get('relays', [])
                #print(relay_addresses)
                if relay_addresses:
                    for item in relay_addresses:
                        #print(item.get('ipv4'))
                        ip = item.get('ipv4')
                        region_name = region_names.get(pop_code.lower(), pop_code.upper())
                        servers[f"{region}-{pop_code.lower()}"] = {
                            'ip': ip,
                            'name': region_name,
                            'code': pop_code.upper()
                        }
        
        if servers:
            print(f"\n{len(servers)} serveurs {region} trouvés")
            return servers
        else:
            print(f"\nAucun serveur {region} trouvé, utilisation des serveurs par défaut")
            return get_fallback_servers()
            
    except requests.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
        print("🔄 Utilisation des serveurs par défaut...")
        return get_fallback_servers()
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"❌ Erreur parsing API: {e}")
        print("🔄 Utilisation des serveurs par défaut...")
        return get_fallback_servers()

def get_fallback_servers():
    """Serveurs EU de secours si l'API ne fonctionne pas"""
    return {
        "eu-west-1": {
            'ip': "155.133.248.34",
            'name': "West Europe 1",
            'code': "EU-W1"
        },
        "eu-west-2": {
            'ip': "155.133.248.50",
            'name': "West Europe 2", 
            'code': "EU-W2"
        },
        "eu-north-1": {
            'ip': "146.66.155.34",
            'name': "North Europe 1",
            'code': "EU-N1"
        },
        "eu-north-2": {
            'ip': "146.66.155.50",
            'name': "North Europe 2",
            'code': "EU-N2"
        },
        "eu-central-1": {
            'ip': "146.66.158.34",
            'name': "Central Europe 1",
            'code': "EU-C1"
        },
        "eu-central-2": {
            'ip': "146.66.158.50",
            'name': "Central Europe 2",
            'code': "EU-C2"
        }
    }

def show_help():
    """Aide détaillée"""
    print("GUIDE PING & RÉSEAU")
    print("=" * 60)
    
    print("\n🏓 PING (LATENCE)")
    print("   • Temps pour envoyer une donnée au serveur")
    print("   • < 15ms  : Excellent (pro level)")
    print("   • < 25ms  : Très bon (matchmaking)")
    print("   • < 35ms  : Correct mais désavantage aux peeks")
    print("   • > 50ms  : Difficile (retard visible)")
    print(color("   • Impact : Plus c'est bas, plus la réaction est rapide", 'yellow'))
    
    print("\n📦 PERTE DE PAQUETS")
    print("   • % de données perdues en route")
    print("   • 0%     : Parfait")
    print("   • < 0.5% : Acceptable")
    print("   • > 1%   : Hitreg défaillant (balles perdues)")
    print(color("   • Impact : Certains tirs n'arrivent pas au serveur", 'yellow'))
    
    print("\n📈 JITTER (INSTABILITÉ)")
    print("   • Variation de la latence")
    print("   • < 5ms  : Stable")
    print("   • < 10ms : Léger")
    print("   • > 15ms : Aim perturbé")
    print(color("   • Impact : Crosshair qui 'saute', aim incohérent", 'yellow'))
    
    print("\n⚡ PICS DE LATENCE")
    print("   • Montées soudaines de ping")
    print("   • Détection : > 3x l'écart-type")
    print(color("   • Impact : Micro-freezes, joueurs qui se téléportent", 'yellow'))
    
    print("\n📊 PERCENTILES")
    print("   • P95 : 95% des pings sont inférieurs")
    print("   • P99 : 99% des pings sont inférieurs")
    print(color("   • Impact : Montre la régularité de la connexion", 'yellow'))
    
    print("\n🎮 POURQUOI C'EST IMPORTANT DANS CS2:")
    print("   • Peeker's advantage : +20ms = désavantage énorme")
    print("   • Hitreg : perte de paquets = balles fantômes")
    print("   • Spray control : jitter = pattern incohérent")
    print("   • Flicks : pics de ping = aim qui lag")
    
    print("\n🔧 SETTINGS RECOMMANDÉS:")
    print("   • rate 786432 (max bandwidth)")
    print("   • cl_cmdrate 128 (envoi au serveur)")
    print("   • cl_updaterate 128 (réception serveur)")
    print("   • cl_interp_ratio 1 (interpolation min)")
    
    print("\n💡 UTILISATION DU SCRIPT:")
    print("   python script.py --eu     # Lister tous les serveurs EU")
    print("   python script.py --us     # Lister tous les serveurs US")
    print("   python script.py -s IP    # Tester un serveur spécifique")
    print("   python script.py -h       # Aide")
    print("   python script.py          # Menu")

def quick_ping_test(server_ip, samples=10):
    """Test rapide pour --list"""
    try:
        responses = ping(server_ip, count=samples, timeout=2)
        times = [resp.time_elapsed * 1000 for resp in responses if resp.success]
        if times:
            return statistics.mean(times), len(times)
        return None, 0
    except:
        return None, 0

def detailed_ping_test(server_ip, samples=500):
    """Test complet pour analyse"""
    try:
        responses = ping(server_ip, count=samples, timeout=3)
        times = [resp.time_elapsed * 1000 for resp in responses if resp.success]
        
        if not times:
            return None
        
        # Statistiques
        loss = (samples - len(times)) / samples * 100
        avg = statistics.mean(times)
        min_ping = min(times)
        max_ping = max(times)
        jitter = statistics.stdev(times) if len(times) > 1 else 0
        
        # Percentiles et pics
        sorted_times = sorted(times)
        p95 = sorted_times[int(0.95 * len(times))]
        p99 = sorted_times[int(0.99 * len(times))]
        spikes = len([t for t in times if t > avg + 3 * jitter])
        
        return {
            'times': times,
            'loss': loss,
            'avg': avg,
            'min': min_ping,
            'max': max_ping,
            'jitter': jitter,
            'p95': p95,
            'p99': p99,
            'spikes': spikes,
            'samples': len(times)
        }
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def list_all_servers(servers, region='eu'):
    """Test rapide des serveurs"""
    region_name = "EUROPE" if region == 'eu' else "US"
    print(f"\n🌍 SCAN SERVEURS {region_name} (Steam API)")
    print("=" * 55)
    
    results = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_server = {
            executor.submit(quick_ping_test, server_data['ip']): (server_id, server_data) 
            for server_id, server_data in servers.items()
        }
        
        for future in as_completed(future_to_server):
            server_id, server_data = future_to_server[future]
            avg_ping, success_count = future.result()
            
            if avg_ping:
                results.append((server_id, server_data, avg_ping, success_count))
                status = "✅" if avg_ping < 35 else "⚠️" if avg_ping < 60 else "❌"
                print(f"{status} {server_data['name']:<15} {server_data['ip']:<15} {avg_ping:5.0f}ms ({success_count}/10)")
            else:
                print(f"❌ {server_data['name']:<15} {server_data['ip']:<15} TIMEOUT")
    
    # Tri par ping croissant
    results.sort(key=lambda x: x[2])
    
    if results:
        print("\n🏆 CLASSEMENT")
        for i, (server_id, server_data, avg_ping, _) in enumerate(results[:3], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"{medal} {server_data['name']} - {avg_ping:.0f}ms")
        
        best_server = results[0]
        print(f"\n💡 RECOMMANDATION: {best_server[1]['name']} ({best_server[2]:.0f}ms)")
        print(f"   Commande: python {sys.argv[0]} -s {best_server[1]['ip']}")

def analyze_results(data):
    """Analyse des résultats"""
    print(f"\n📊 RÉSULTATS")
    print('-----------------------')
    print(f"Perte        : {data['loss']:.1f}% ({data['samples']}/500)")
    print(f"Ping moyen   : {data['avg']:.0f}ms")
    print(f"Min / Max    : {data['min']:.0f} / {data['max']:.0f}ms")
    print(f"Jitter       : {data['jitter']:.1f}ms")
    print(f"95e percentile: {data['p95']:.0f}ms")
    print(f"99e percentile: {data['p99']:.0f}ms")
    print(f"Pics détectés: {data['spikes']}")
    
    # VERDICT CS2
    print(f"\n🎯 VERDICT")
    print('-----------------------')
    
    critical_issues = []
    warnings = []
    
    if data['loss'] > 0.5:
        critical_issues.append(f"Perte {data['loss']:.1f}% → hitreg défaillant")
    if data['avg'] > 35:
        critical_issues.append(f"Ping {data['avg']:.0f}ms → désavantage peek")
    if data['max'] > 80:
        critical_issues.append(f"Pic {data['max']:.0f}ms → freeze possible")
    if data['jitter'] > 8:
        critical_issues.append(f"Jitter {data['jitter']:.1f}ms → aim instable")
    if data['p99'] > 60:
        critical_issues.append(f"P99 {data['p99']:.0f}ms → lags réguliers")
    if data['spikes'] > 2:
        critical_issues.append(f"{data['spikes']} pics → micro-freezes")
    
    if data['avg'] > 25:
        warnings.append("Ping élevé pour le compétitif")
    if data['jitter'] > 5:
        warnings.append("Micro-variations détectées")
    if data['p95'] > 45:
        warnings.append("Quelques ralentissements")
    
    if critical_issues:
        for issue in critical_issues:
            print(color(f"   • {issue}", 'yellow'))
        print("\n🔧 ACTIONS:")
        print('-----------------------')
        print("   • Changer de serveur/région")
        print("   • Vérifier rate/interp settings")
        print("   • Tester connexion Ethernet")
    elif warnings:
        for warning in warnings:
            print(f"   • {warning}")
        print("\n💡 RECOMMANDATIONS:")
        print('-----------------------')
        print("   • Éviter les duels serrés")
        print("   • Privilégier le jeu défensif")
        if data['avg'] > 25:
            print("   • Considérer un serveur plus proche")
    else:
        if data['avg'] <= 15:
            print("   🏆 Ping excellent pour le pro play")
        elif data['avg'] <= 25:
            print("   🎯 Parfait pour le matchmaking")
        print("   ⚡ Hitreg fiable • Peeks réactifs")
    
    # Analyse technique
    print(f"\n⚙️  DÉTAILS TECHNIQUES")
    print('-----------------------')
    print(f"Variation max    : {data['max'] - data['min']:.0f}ms")
    print(f"Stabilité        : {100 - (data['jitter']/data['avg']*100):.0f}%")
    
    # Grade CS2
    if data['avg'] <= 5:
        latency_grade = color("S+ (LAN-like)", 'green')
    elif data['avg'] <= 15:
        latency_grade = color("S (Pro level)", 'green')
    elif data['avg'] <= 25:
        latency_grade = color("A (Excellent)", 'green')
    elif data['avg'] <= 35:
        latency_grade = color("B (Correct)", 'yellow')
    elif data['avg'] <= 50:
        latency_grade = color("C (Difficile)", 'red')
    else:
        latency_grade = color("D (Injouable)", 'red')
    
    print(f"Grade        : {latency_grade}\n\n")

def show_main_menu():
    """Menu principal"""
    print("\n\nCS2 NETWORK ANALYZER\n")
    print("=" * 40)
    print(color("\n1. 🌍 Lister les serveurs EU", 'yellow'))
    print(color("2. 🌍 Lister les serveurs US", 'yellow'))
    print(color("3. 📚 Guide réseau", 'yellow'))
    print(color("4. 🎮 Tester un serveur spécifique", 'yellow'))
    print(color("5. ❌ Quitter", 'red'))
    
    while True:
        try:
            choice = input("\nChoix (1-5): ").strip()
            
            if choice == "1":
                servers = fetch_cs2_servers('eu')
                list_all_servers(servers, 'eu')
                break            
            elif choice == "2":
                servers = fetch_cs2_servers('us')
                list_all_servers(servers, 'us')
                break
            elif choice == "3":
                show_help()
                break
            elif choice == "4":
                servers = fetch_cs2_servers('eu')
                show_server_menu(servers)
                break
            elif choice == "5":
                print("Au revoir !")
                sys.exit(0)
            else:
                print(color("Choix invalide (1-5)", 'red'))
        except KeyboardInterrupt:
            print("\nAu revoir !")
            break

def show_server_menu(servers):
    """Menu de sélection de serveur"""
    print("\n🎮 SERVEURS DISPONIBLES:")
    server_list = list(servers.items())
    
    for i, (server_id, server_data) in enumerate(server_list, 1):
        print(f"{i:2}. {server_data['name']:<15} ({server_data['ip']})")
    
    print(f"{len(servers)+1:2}. IP personnalisée")
    
    while True:
        try:
            choice = input(f"\nChoisir un serveur (1-{len(servers)+1}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(servers):
                    server_id, server_data = server_list[choice_num - 1]
                    run_detailed_test(server_data['name'], server_data['ip'])
                    break
                elif choice_num == len(servers) + 1:
                    custom_ip = input("IP du serveur: ").strip()
                    if custom_ip:
                        run_detailed_test(f"Serveur personnalisé", custom_ip)
                        break
                    else:
                        print(color("❌ IP invalide", 'red'))
                else:
                    print(f"❌ Choix invalide (1-{len(servers)+1})")
            else:
                print(f"❌ Entrez un nombre (1-{len(servers)+1})")
        except KeyboardInterrupt:
            print("\n👋 Retour au menu")
            break

def run_detailed_test(server_name, server_ip):
    """Lance un test détaillé"""
    print(f"\n Test du serveur → {server_name} ({server_ip})")
    print("=" * 50)
    
    data = detailed_ping_test(server_ip)
    
    if data:
        analyze_results(data)
    else:
        print(color("SERVEUR INACCESSIBLE", 'red'))

def main():
    parser = argparse.ArgumentParser(
        description="Test de ping optimisé pour CS2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python script.py              # Menu principal
  python script.py --eu       # Liste des serveurs EU
  python script.py --us       # Liste des serveurs US
  python script.py -s 1.2.3.4   # Tester un serveur spécifique
  python script.py -h           # Guide réseau
        """
    )
    
    parser.add_argument("-s", "--server", help="IP du serveur à tester")
    parser.add_argument("--eu", action="store_true", help="Lister les serveurs EU")
    parser.add_argument("--us", action="store_true", help="Lister les serveurs US")
    
    # Override help pour afficher notre guide
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        show_help()
        return
    
    args = parser.parse_args()
    
    # Récupération des serveurs CS2
    if args.eu:
        servers = fetch_cs2_servers('eu')
        list_all_servers(servers, 'eu')
    elif args.us:
        servers = fetch_cs2_servers('us')
        list_all_servers(servers, 'us')
    elif args.server:
        run_detailed_test(f"Serveur personnalisé", args.server)
    else:
        show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color("\nTest interrompu", 'red'))
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        print("Vérifiez: connexion internet, pythonping et requests installés")
        print("Installation: pip install pythonping requests")